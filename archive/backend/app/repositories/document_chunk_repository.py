from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


class DocumentChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, document_text_id, chunk_index: int, text: str):
        chunk = DocumentChunk(
            document_text_id=document_text_id,
            chunk_index=chunk_index,
            text=text,
            character_count=len(text),
            token_estimate=max(1, len(text) // 4),
        )

        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)

        return chunk

    def list_for_document_text(self, document_text_id):
        result = self.db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_text_id == document_text_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )

        return list(result.scalars().all())
