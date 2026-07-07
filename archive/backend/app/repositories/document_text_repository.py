from sqlalchemy.orm import Session

from app.models.document_text import DocumentText


class DocumentTextRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, document_id, text: str):
        row = DocumentText(
            document_id=document_id,
            text=text,
            character_count=len(text),
        )

        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        return row
