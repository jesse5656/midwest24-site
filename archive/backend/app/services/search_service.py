from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.entity import Entity


class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_entities(self, query: str):
        normalized_query = f"%{query.strip()}%"

        result = self.db.execute(
            select(Entity)
            .where(
                or_(
                    Entity.title.ilike(normalized_query),
                    Entity.description.ilike(normalized_query),
                    Entity.entity_type.ilike(normalized_query),
                    Entity.status.ilike(normalized_query),
                )
            )
            .order_by(Entity.created_at.desc())
        )

        return list(result.scalars().all())
