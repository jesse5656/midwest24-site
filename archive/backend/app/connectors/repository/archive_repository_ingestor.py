from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.connectors.repository.allowlist import RepositoryAllowlist
from app.connectors.repository.config import get_repository_allowed_roots
from app.connectors.repository.duplicate_detector import RepositoryDuplicateDetector
from app.connectors.repository.filesystem_repository_connector import (
    RepositoryFile,
    RepositoryFilesystemConnector,
)
from app.connectors.repository.ingestion_report import (
    RepositoryIngestionFailure,
    RepositoryIngestionReport,
)
from app.connectors.repository.job_statistics import RepositoryProcessingJobStatistics
from app.connectors.repository.path_validator import RepositoryPathValidator
from app.core.config import settings
from app.repositories.document_repository import DocumentRepository
from app.repositories.entity_repository import EntityRepository
from app.schemas.processing_job import ProcessingJobCreate
from app.services.processing_job_service import ProcessingJobService


REPOSITORY_DOCUMENT_JOB_TYPE = "repository_document_ingestion"

logger = logging.getLogger(__name__)


class ArchiveRepositoryIngestor:
    """
    Ingests supported files from a local repository into the existing Archive pipeline.

    Scope:
    - Discover repository files.
    - Validate the repository path.
    - Enforce configured allowed roots.
    - Report skipped paths, unsupported files, duplicates, failures, bytes, elapsed time, and job status counts.
    - Copy new supported files into Archive document storage.
    - Create Document rows tied to the provided entity.
    - Create ProcessingJob rows for each new document.

    Explicitly deferred:
    - Git history.
    - Git blame.
    - Commit graph analysis.
    - Branch analysis.
    - Code intelligence.
    """

    def __init__(self, db: Session):
        self.db = db
        self.entity_repository = EntityRepository(db)
        self.document_repository = DocumentRepository(db)
        self.processing_job_service = ProcessingJobService(db)

    def ingest_repository(
        self,
        entity_id: UUID,
        repository_path: str | Path,
    ) -> RepositoryIngestionReport:
        if self.entity_repository.get(entity_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

        started_at = time.perf_counter()

        repository_path = RepositoryPathValidator.validate(repository_path)
        repository_path = RepositoryAllowlist(get_repository_allowed_roots()).validate(repository_path)

        logger.info(
            "Repository ingestion started",
            extra={"repository_path": str(repository_path), "entity_id": str(entity_id)},
        )

        connector = RepositoryFilesystemConnector(repository_path)
        discovery_report = connector.discover_with_report()
        discovered_files = discovery_report.supported_files

        new_files, duplicate_files = RepositoryDuplicateDetector(self.db).filter_new_files(
            entity_id=entity_id,
            repository_files=discovered_files,
        )

        storage_root = Path(settings.document_storage_root)
        storage_root.mkdir(parents=True, exist_ok=True)

        document_count = 0
        processing_job_count = 0
        created_document_ids = []
        bytes_ingested = 0
        failures: list[RepositoryIngestionFailure] = []

        for repository_file in new_files:
            try:
                document = self._create_document_from_repository_file(
                    entity_id=entity_id,
                    repository_file=repository_file,
                    storage_root=storage_root,
                )
                document_count += 1
                created_document_ids.append(document.id)
                bytes_ingested += repository_file.size_bytes

                self.processing_job_service.create_job(
                    ProcessingJobCreate(
                        document_id=document.id,
                        job_type=REPOSITORY_DOCUMENT_JOB_TYPE,
                        priority=100,
                    )
                )
                processing_job_count += 1

            except Exception as exc:
                failures.append(
                    RepositoryIngestionFailure(
                        path=repository_file.relative_path,
                        reason=str(exc),
                    )
                )
                logger.exception(
                    "Repository file ingestion failed",
                    extra={
                        "repository_path": str(repository_path),
                        "repository_file": repository_file.relative_path,
                        "entity_id": str(entity_id),
                    },
                )

        processing_jobs_by_status = RepositoryProcessingJobStatistics(self.db).count_for_documents(
            created_document_ids
        )

        elapsed_ms = int((time.perf_counter() - started_at) * 1000)

        report = RepositoryIngestionReport(
            discovered_count=len(discovered_files),
            document_count=document_count,
            processing_job_count=processing_job_count,
            bytes_ingested=bytes_ingested,
            elapsed_ms=elapsed_ms,
            skipped_count=discovery_report.skipped_count,
            unsupported_count=discovery_report.unsupported_count,
            duplicate_count=len(duplicate_files),
            failures=failures,
            skipped_paths=discovery_report.skipped_paths,
            unsupported_files=discovery_report.unsupported_files,
            duplicate_files=duplicate_files,
            processing_jobs_by_status=processing_jobs_by_status,
        )

        logger.info(
            "Repository ingestion finished",
            extra={
                "repository_path": str(repository_path),
                "entity_id": str(entity_id),
                "discovered_count": report.discovered_count,
                "document_count": report.document_count,
                "processing_job_count": report.processing_job_count,
                "bytes_ingested": report.bytes_ingested,
                "elapsed_ms": report.elapsed_ms,
                "skipped_count": report.skipped_count,
                "unsupported_count": report.unsupported_count,
                "duplicate_count": report.duplicate_count,
                "failure_count": len(report.failures),
            },
        )

        return report

    def _create_document_from_repository_file(
        self,
        entity_id: UUID,
        repository_file: RepositoryFile,
        storage_root: Path,
    ):
        safe_name = repository_file.relative_path.replace("/", "__")
        storage_name = f"{uuid4()}-{safe_name}"
        storage_path = storage_root / storage_name

        shutil.copyfile(repository_file.path, storage_path)

        return self.document_repository.create(
            entity_id=entity_id,
            filename=repository_file.relative_path,
            mime_type=self._guess_mime_type(repository_file),
            storage_path=str(storage_path),
        )

    def _guess_mime_type(self, repository_file: RepositoryFile) -> str:
        if repository_file.suffix == ".md":
            return "text/markdown"
        if repository_file.suffix == ".txt":
            return "text/plain"
        if repository_file.suffix in {".yml", ".yaml"}:
            return "application/x-yaml"
        if repository_file.suffix == ".json":
            return "application/json"
        if repository_file.suffix == ".html":
            return "text/html"
        if repository_file.suffix == ".css":
            return "text/css"
        if repository_file.suffix in {".py", ".js", ".ts", ".tsx", ".jsx"}:
            return "text/plain"
        return "application/octet-stream"


ArchiveRepositoryIngestionResult = RepositoryIngestionReport
