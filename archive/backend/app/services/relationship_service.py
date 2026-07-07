from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.entity_repository import EntityRepository
from app.repositories.relationship_repository import RelationshipRepository
from app.schemas.relationship import RelationshipCreate


class RelationshipService:
    def __init__(self, db: Session):
        self.entity_repository = EntityRepository(db)
        self.relationship_repository = RelationshipRepository(db)

    def create_relationship(self, data: RelationshipCreate):
        if data.source_entity_id == data.target_entity_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Relationship source and target cannot be the same entity",
            )

        if self.entity_repository.get(data.source_entity_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source entity not found")

        if self.entity_repository.get(data.target_entity_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target entity not found")

        return self.relationship_repository.create(data)

    def list_relationships(self):
        return self.relationship_repository.list_all()

    def list_entity_relationships(self, entity_id: UUID):
        if self.entity_repository.get(entity_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

        return self.relationship_repository.list_for_entity(entity_id)
