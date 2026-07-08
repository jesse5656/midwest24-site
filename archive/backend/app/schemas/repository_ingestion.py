from uuid import UUID

from pydantic import BaseModel, Field


class RepositoryIngestionCreate(BaseModel):
    entity_id: UUID
    repository_path: str = Field(..., min_length=1)


class RepositoryIngestionResponse(BaseModel):
    discovered_count: int
    document_count: int
    processing_job_count: int
