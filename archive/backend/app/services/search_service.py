from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.entity import Entity


class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_entities(self, query: str):
        cleaned_query = query.strip()

        if not cleaned_query:
            return []

        search_vector = func.to_tsvector(
            "english",
            func.concat_ws(
                " ",
                Entity.title,
                Entity.description,
                Entity.entity_type,
                Entity.status,
            ),
        )

        search_query = func.plainto_tsquery("english", cleaned_query)

        result = self.db.execute(
            select(Entity)
            .where(
                or_(
                    search_vector.op("@@")(search_query),
                    Entity.title.ilike(f"%{cleaned_query}%"),
                    Entity.description.ilike(f"%{cleaned_query}%"),
                )
            )
            .order_by(Entity.created_at.desc())
        )

        return list(result.scalars().all())
