from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
    ".cache",
}

DEFAULT_INCLUDED_SUFFIXES = {
    ".md",
    ".txt",
    ".rst",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
}


@dataclass(frozen=True)
class RepositoryFile:
    path: Path
    relative_path: str
    suffix: str
    size_bytes: int


class RepositoryFilesystemConnector:
    """
    Discovers ingestible files from a local repository.

    This connector intentionally performs repository filesystem discovery only.
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
        if not self.root_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {self.root_path}")

        if not self.root_path.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {self.root_path}")

        discovered: list[RepositoryFile] = []

        for file_path in sorted(self.root_path.rglob("*")):
            if not file_path.is_file():
                continue

            if self._is_excluded(file_path):
                continue

            if file_path.suffix not in self.included_suffixes:
                continue

            stat = file_path.stat()
            discovered.append(
                RepositoryFile(
                    path=file_path,
                    relative_path=file_path.relative_to(self.root_path).as_posix(),
                    suffix=file_path.suffix,
                    size_bytes=stat.st_size,
                )
            )

        return discovered

    def _is_excluded(self, file_path: Path) -> bool:
        relative_parts = file_path.relative_to(self.root_path).parts
        return any(part in self.excluded_dirs for part in relative_parts)
