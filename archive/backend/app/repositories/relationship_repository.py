from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.relationship import Relationship
from app.schemas.relationship import RelationshipCreate


class RelationshipRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: RelationshipCreate) -> Relationship:
        relationship = Relationship(**data.model_dump())
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship

    def list_all(self) -> list[Relationship]:
        result = self.db.execute(select(Relationship).order_by(Relationship.created_at.desc()))
        return list(result.scalars().all())

    def list_for_entity(self, entity_id: UUID) -> list[Relationship]:
        result = self.db.execute(
            select(Relationship)
            .where(
                or_(
                    Relationship.source_entity_id == entity_id,
                    Relationship.target_entity_id == entity_id,
                )
            )
            .order_by(Relationship.created_at.desc())
        )
        return list(result.scalars().all())
