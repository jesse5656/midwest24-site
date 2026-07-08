from __future__ import annotations

from dataclasses import dataclass, field

from app.connectors.repository.discovery_report import (
    RepositorySkippedPath,
    RepositoryUnsupportedFile,
)
from app.connectors.repository.job_statistics import ProcessingJobStatusCounts


@dataclass(frozen=True)
class RepositoryIngestionFailure:
    path: str
    reason: str


@dataclass(frozen=True)
class RepositoryIngestionReport:
    discovered_count: int = 0
    document_count: int = 0
    processing_job_count: int = 0
    bytes_ingested: int = 0
    elapsed_ms: int = 0
    skipped_count: int = 0
    unsupported_count: int = 0
    failures: list[RepositoryIngestionFailure] = field(default_factory=list)
    skipped_paths: list[RepositorySkippedPath] = field(default_factory=list)
    unsupported_files: list[RepositoryUnsupportedFile] = field(default_factory=list)
    processing_jobs_by_status: ProcessingJobStatusCounts = field(default_factory=ProcessingJobStatusCounts)
