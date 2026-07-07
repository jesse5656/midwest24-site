from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import TagCreate


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: TagCreate) -> Tag:
        tag = Tag(name=data.name.strip().lower())
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def list_all(self) -> list[Tag]:
        result = self.db.execute(select(Tag).order_by(Tag.name.asc()))
        return list(result.scalars().all())

    def get_by_name(self, name: str) -> Tag | None:
        result = self.db.execute(select(Tag).where(Tag.name == name.strip().lower()))
        return result.scalar_one_or_none()


    def get(self, tag_id: UUID) -> Tag | None:
        return self.db.get(Tag, tag_id)
