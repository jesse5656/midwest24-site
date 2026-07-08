from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.connectors.repository.discovery_report import (
    DEFAULT_REPOSITORY_EXCLUDED_DIRS,
    DEFAULT_REPOSITORY_INCLUDED_SUFFIXES,
    RepositoryDiscoveryReport,
    RepositorySkippedPath,
    RepositoryUnsupportedFile,
)


DEFAULT_EXCLUDED_DIRS = DEFAULT_REPOSITORY_EXCLUDED_DIRS
DEFAULT_INCLUDED_SUFFIXES = DEFAULT_REPOSITORY_INCLUDED_SUFFIXES


@dataclass(frozen=True)
class RepositoryFile:
    path: Path
    relative_path: str
    suffix: str
    size_bytes: int


class RepositoryFilesystemConnector:
    """
    Discovers ingestible files from a local repository.

    This connector performs repository filesystem discovery only.
    It does not inspect git history, parse commits, analyze authorship, or bypass
    the Archive ingestion pipeline.
    """

    def __init__(
        self,
        root_path: str | Path,
        included_suffixes: Iterable[str] | None = None,
        excluded_dirs: Iterable[str] | None = None,
    ) -> None:
        self.root_path = Path(root_path).expanduser().resolve()
        self.included_suffixes = set(included_suffixes or DEFAULT_INCLUDED_SUFFIXES)
        self.excluded_dirs = set(excluded_dirs or DEFAULT_EXCLUDED_DIRS)

    def discover(self) -> list[RepositoryFile]:
        return self.discover_with_report().supported_files

    def discover_with_report(self) -> RepositoryDiscoveryReport:
        if not self.root_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {self.root_path}")

        if not self.root_path.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {self.root_path}")

        supported_files: list[RepositoryFile] = []
        skipped_paths: list[RepositorySkippedPath] = []
        unsupported_files: list[RepositoryUnsupportedFile] = []

        for path in sorted(self.root_path.rglob("*")):
            relative_path = path.relative_to(self.root_path).as_posix()

            excluded_part = self._excluded_part(path)
            if excluded_part:
                if path.is_dir():
                    skipped_paths.append(
                        RepositorySkippedPath(
                            path=relative_path,
                            reason=f"excluded_directory:{excluded_part}",
                        )
                    )
                continue

            if not path.is_file():
                continue

            if path.suffix not in self.included_suffixes:
                unsupported_files.append(
                    RepositoryUnsupportedFile(
                        path=relative_path,
                        suffix=path.suffix,
                    )
                )
                continue

            stat = path.stat()
            supported_files.append(
                RepositoryFile(
                    path=path,
                    relative_path=relative_path,
                    suffix=path.suffix,
                    size_bytes=stat.st_size,
                )
            )

        return RepositoryDiscoveryReport(
            supported_files=supported_files,
            skipped_paths=skipped_paths,
            unsupported_files=unsupported_files,
        )

    def _excluded_part(self, file_path: Path) -> str | None:
        relative_parts = file_path.relative_to(self.root_path).parts

        for part in relative_parts:
            if part in self.excluded_dirs:
                return part

        return None

    def _is_excluded(self, file_path: Path) -> bool:
        return self._excluded_part(file_path) is not None
