from uuid import UUID

from pydantic import BaseModel, Field


class RepositoryIngestionCreate(BaseModel):
    entity_id: UUID
    repository_path: str = Field(..., min_length=1)


class RepositoryIngestionFailureResponse(BaseModel):
    path: str
    reason: str


class ProcessingJobStatusCountsResponse(BaseModel):
    pending: int
    running: int
    completed: int
    failed: int
    total: int


class RepositoryIngestionResponse(BaseModel):
    discovered_count: int
    document_count: int
    processing_job_count: int
    bytes_ingested: int
    elapsed_ms: int
    skipped_count: int
    unsupported_count: int
    failures: list[RepositoryIngestionFailureResponse]
    processing_jobs_by_status: ProcessingJobStatusCountsResponse
