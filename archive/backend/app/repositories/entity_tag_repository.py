from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entity_tag import EntityTag
from app.schemas.entity_tag import EntityTagCreate


class EntityTagRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: EntityTagCreate) -> EntityTag:
        row = EntityTag(**data.model_dump())

        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        return row

    def list_for_entity(self, entity_id: UUID) -> list[EntityTag]:
        result = self.db.execute(
            select(EntityTag).where(EntityTag.entity_id == entity_id)
        )

        return list(result.scalars().all())
