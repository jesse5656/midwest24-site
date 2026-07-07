from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.tag_repository import TagRepository
from app.schemas.tag import TagCreate


class TagService:
    def __init__(self, db: Session):
        self.repository = TagRepository(db)

    def create_tag(self, data: TagCreate):
        existing = self.repository.get_by_name(data.name)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists")

        return self.repository.create(data)

    def list_tags(self):
        return self.repository.list_all()
