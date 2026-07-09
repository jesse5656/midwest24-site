from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.change_detector import RepositoryChangeSet
from app.connectors.repository.ingestion_report import RepositoryIngestionReport


@dataclass(frozen=True)
class RepositoryIncrementalIngestionReport:
    changes: RepositoryChangeSet
    manifest_updated: bool
    ingestion_report: RepositoryIngestionReport | None

    @property
    def new_count(self) -> int:
        return len(self.changes.new_files)

    @property
    def modified_count(self) -> int:
        return len(self.changes.modified_files)

    @property
    def deleted_count(self) -> int:
        return len(self.changes.deleted_files)

    @property
    def unchanged_count(self) -> int:
        return len(self.changes.unchanged_files)

    @property
    def changed_count(self) -> int:
        return self.changes.changed_count

    @property
    def ingested_document_count(self) -> int:
        if self.ingestion_report is None:
            return 0
        return self.ingestion_report.document_count

    @property
    def processing_job_count(self) -> int:
        if self.ingestion_report is None:
            return 0
        return self.ingestion_report.processing_job_count
