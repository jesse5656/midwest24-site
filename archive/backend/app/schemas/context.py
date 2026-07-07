from pydantic import BaseModel

from app.schemas.entity import EntityResponse
from app.schemas.relationship import RelationshipResponse
from app.schemas.entity_tag import EntityTagResponse


class EntityContextResponse(BaseModel):
    entity: EntityResponse
    relationships: list[RelationshipResponse]
    tags: list[EntityTagResponse]
