from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RelationshipCreate(BaseModel):
    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: str = Field(..., min_length=1, max_length=100)


class RelationshipResponse(BaseModel):
    id: UUID
    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
