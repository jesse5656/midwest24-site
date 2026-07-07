from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProcessingJobCreate(BaseModel):
    document_id: UUID
    job_type: str = Field(..., min_length=1, max_length=100)
    priority: int = 100


class ProcessingJobResponse(BaseModel):
    id: UUID
    document_id: UUID
    job_type: str
    status: str
    progress: int
    worker: str | None
    error: str | None
    priority: int
    retry_count: int
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
