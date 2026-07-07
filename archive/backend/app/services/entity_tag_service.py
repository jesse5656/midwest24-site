from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.entity_repository import EntityRepository
from app.repositories.entity_tag_repository import EntityTagRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.entity_tag import EntityTagCreate


class EntityTagService:
    def __init__(self, db: Session):
        self.entity_repository = EntityRepository(db)
        self.tag_repository = TagRepository(db)
        self.entity_tag_repository = EntityTagRepository(db)

    def attach_tag(self, data: EntityTagCreate):
        if self.entity_repository.get(data.entity_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

        tag = self.tag_repository.get(data.tag_id)
        if tag is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

        return self.entity_tag_repository.create(data)

    def list_entity_tags(self, entity_id: UUID):
        if self.entity_repository.get(entity_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

        return self.entity_tag_repository.list_for_entity(entity_id)
