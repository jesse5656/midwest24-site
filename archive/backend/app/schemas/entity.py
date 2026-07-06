from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EntityCreate(BaseModel):
    entity_type: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: str = Field(default="active", max_length=50)


class EntityUpdate(BaseModel):
    entity_type: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = Field(default=None, max_length=50)


class EntityResponse(BaseModel):
    id: UUID
    entity_type: str
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
