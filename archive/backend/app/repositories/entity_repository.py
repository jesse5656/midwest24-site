from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entity import Entity
from app.schemas.entity import EntityCreate, EntityUpdate


class EntityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: EntityCreate) -> Entity:
        entity = Entity(**data.model_dump())
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def list(self) -> list[Entity]:
        result = self.db.execute(select(Entity).order_by(Entity.created_at.desc()))
        return list(result.scalars().all())

    def get(self, entity_id: UUID) -> Entity | None:
        return self.db.get(Entity, entity_id)

    def update(self, entity: Entity, data: EntityUpdate) -> Entity:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(entity, key, value)

        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: Entity) -> None:
        self.db.delete(entity)
        self.db.commit()
