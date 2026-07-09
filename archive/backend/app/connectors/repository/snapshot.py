from __future__ import annotations

from pathlib import Path

from app.connectors.repository.file_fingerprint import RepositoryFileFingerprinter
from app.connectors.repository.filesystem_repository_connector import RepositoryFilesystemConnector
from app.connectors.repository.manifest import RepositoryManifest, RepositoryManifestEntry


class RepositorySnapshotter:
    def __init__(self, fingerprinter: RepositoryFileFingerprinter | None = None):
        self.fingerprinter = fingerprinter or RepositoryFileFingerprinter()

    def snapshot(self, repository_path: str | Path) -> RepositoryManifest:
        repository_path = Path(repository_path).expanduser().resolve()

        connector = RepositoryFilesystemConnector(repository_path)
        files = connector.discover()

        entries = {}

        for file in files:
            entries[file.relative_path] = RepositoryManifestEntry(
                path=file.relative_path,
                fingerprint=self.fingerprinter.fingerprint(file.path),
                size_bytes=file.size_bytes,
                suffix=file.suffix,
            )

        return RepositoryManifest(
            repository_path=str(repository_path),
            entries=entries,
        )
