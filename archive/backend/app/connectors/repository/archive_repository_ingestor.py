from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.connectors.repository.path_validator import RepositoryPathValidator
from app.connectors.repository.filesystem_repository_connector import (
    RepositoryFile,
    RepositoryFilesystemConnector,
)
from app.core.config import settings
from app.repositories.document_repository import DocumentRepository
from app.repositories.entity_repository import EntityRepository
from app.schemas.processing_job import ProcessingJobCreate
from app.services.processing_job_service import ProcessingJobService


REPOSITORY_DOCUMENT_JOB_TYPE = "repository_document_ingestion"


@dataclass(frozen=True)
class ArchiveRepositoryIngestionResult:
    discovered_count: int
    document_count: int
    processing_job_count: int


class ArchiveRepositoryIngestor:
    """
    Ingests supported files from a local repository into the existing Archive pipeline.

    Scope:
    - Discover repository files.
    - Copy each supported file into Archive document storage.
    - Create a Document row tied to the provided entity.
    - Create a ProcessingJob row for each document.

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

    def ingest_repository(self, entity_id: UUID, repository_path: str | Path) -> ArchiveRepositoryIngestionResult:
        if self.entity_repository.get(entity_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

        repository_path = RepositoryPathValidator.validate(repository_path)
        connector = RepositoryFilesystemConnector(repository_path)
        discovered_files = connector.discover()

        storage_root = Path(settings.document_storage_root)
        storage_root.mkdir(parents=True, exist_ok=True)

        document_count = 0
        processing_job_count = 0

        for repository_file in discovered_files:
            document = self._create_document_from_repository_file(
                entity_id=entity_id,
                repository_file=repository_file,
                storage_root=storage_root,
            )
            document_count += 1

            self.processing_job_service.create_job(
                ProcessingJobCreate(
                    document_id=document.id,
                    job_type=REPOSITORY_DOCUMENT_JOB_TYPE,
                    priority=100,
                )
            )
            processing_job_count += 1

        return ArchiveRepositoryIngestionResult(
            discovered_count=len(discovered_files),
            document_count=document_count,
            processing_job_count=processing_job_count,
        )

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
