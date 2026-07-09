from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.repository_ingestion import RepositoryIngestionResponse
from app.schemas.repository_operator_summary import RepositoryIncrementalOperatorSummaryResponse


class RepositoryIncrementalIngestionCreate(BaseModel):
    entity_id: UUID
    repository_path: str = Field(..., min_length=1)
    manifest_path: str = Field(..., min_length=1)


class RepositoryChangeSetResponse(BaseModel):
    new_files: list[str]
    modified_files: list[str]
    deleted_files: list[str]
    unchanged_files: list[str]
    changed_files: list[str]
    changed_count: int


class RepositoryIncrementalIngestionResponse(BaseModel):
    changes: RepositoryChangeSetResponse
    manifest_updated: bool
    ingestion_report: RepositoryIngestionResponse | None
    new_count: int
    modified_count: int
    deleted_count: int
    unchanged_count: int
    changed_count: int
    ingested_document_count: int
    processing_job_count: int
    summary: RepositoryIncrementalOperatorSummaryResponse | None = None
