from __future__ import annotations

import os
import tempfile
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.connectors.repository.archive_repository_ingestor import ArchiveRepositoryIngestor
from app.connectors.repository.change_detector import RepositoryChangeDetector
from app.connectors.repository.config import REPOSITORY_ALLOWED_ROOTS_ENV
from app.connectors.repository.incremental_report import RepositoryIncrementalIngestionReport
from app.connectors.repository.manifest import RepositoryManifestStore
from app.connectors.repository.snapshot import RepositorySnapshotter


class RepositoryIncrementalIngestor:
    def __init__(
        self,
        db: Session,
        manifest_store: RepositoryManifestStore,
        snapshotter: RepositorySnapshotter | None = None,
    ):
        self.db = db
        self.manifest_store = manifest_store
        self.snapshotter = snapshotter or RepositorySnapshotter()

    def ingest_changed_repository(
        self,
        entity_id: UUID,
        repository_path: str | Path,
    ) -> RepositoryIncrementalIngestionReport:
        repository_path = Path(repository_path).expanduser().resolve()

        previous = self.manifest_store.load()
        current = self.snapshotter.snapshot(repository_path)
        changes = RepositoryChangeDetector().compare(previous, current)

        ingestion_report = None

        if changes.new_files or changes.modified_files:
            with tempfile.TemporaryDirectory(dir=repository_path.parent) as temp_dir:
                changed_repository = Path(temp_dir) / repository_path.name
                changed_repository.mkdir(parents=True, exist_ok=True)

                for relative_path in changes.changed_files:
                    source = repository_path / relative_path
                    destination = changed_repository / relative_path
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(source.read_bytes())

                previous_allowed_roots = os.environ.get(REPOSITORY_ALLOWED_ROOTS_ENV)

                try:
                    if previous_allowed_roots:
                        os.environ[REPOSITORY_ALLOWED_ROOTS_ENV] = (
                            previous_allowed_roots + os.pathsep + str(Path(temp_dir).resolve())
                        )

                    ingestion_report = ArchiveRepositoryIngestor(self.db).ingest_repository(
                        entity_id=entity_id,
                        repository_path=changed_repository,
                    )
                finally:
                    if previous_allowed_roots is None:
                        os.environ.pop(REPOSITORY_ALLOWED_ROOTS_ENV, None)
                    else:
                        os.environ[REPOSITORY_ALLOWED_ROOTS_ENV] = previous_allowed_roots

        self.manifest_store.save(current)

        return RepositoryIncrementalIngestionReport(
            changes=changes,
            manifest_updated=True,
            ingestion_report=ingestion_report,
        )
