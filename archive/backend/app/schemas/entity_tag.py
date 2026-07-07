from uuid import UUID

from pydantic import BaseModel


class EntityTagCreate(BaseModel):
    entity_id: UUID
    tag_id: UUID


class EntityTagResponse(BaseModel):
    id: UUID
    entity_id: UUID
    tag_id: UUID

    model_config = {"from_attributes": True}
