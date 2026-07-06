from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.entity_repository import EntityRepository
from app.schemas.entity import EntityCreate, EntityUpdate


class EntityService:
    def __init__(self, db: Session):
        self.repository = EntityRepository(db)

    def create_entity(self, data: EntityCreate):
        return self.repository.create(data)

    def list_entities(self):
        return self.repository.list()

    def get_entity(self, entity_id: UUID):
        entity = self.repository.get(entity_id)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
        return entity

    def update_entity(self, entity_id: UUID, data: EntityUpdate):
        entity = self.get_entity(entity_id)
        return self.repository.update(entity, data)

    def delete_entity(self, entity_id: UUID) -> None:
        entity = self.get_entity(entity_id)
        self.repository.delete(entity)
