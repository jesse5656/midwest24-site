from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, entity_id: UUID, filename: str, mime_type: str | None, storage_path: str) -> Document:
        document = Document(
            entity_id=entity_id,
            filename=filename,
            mime_type=mime_type,
            storage_path=storage_path,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def list_for_entity(self, entity_id: UUID) -> list[Document]:
        result = self.db.execute(
            select(Document)
            .where(Document.entity_id == entity_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())


    def get(self, document_id: UUID) -> Document | None:
        return self.db.get(Document, document_id)
