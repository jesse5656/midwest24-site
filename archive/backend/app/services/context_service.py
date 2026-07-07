from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.entity_repository import EntityRepository
from app.repositories.relationship_repository import RelationshipRepository
from app.repositories.entity_tag_repository import EntityTagRepository


class ContextService:
    def __init__(self, db: Session):
        self.entity_repository = EntityRepository(db)
        self.relationship_repository = RelationshipRepository(db)
        self.entity_tag_repository = EntityTagRepository(db)

    def get_context(self, entity_id: UUID):
        entity = self.entity_repository.get(entity_id)

        if entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entity not found",
            )

        return {
            "entity": entity,
            "relationships": self.relationship_repository.list_for_entity(entity_id),
            "tags": self.entity_tag_repository.list_for_entity(entity_id),
        }
