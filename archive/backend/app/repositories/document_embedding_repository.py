import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_embedding import DocumentEmbedding


class DocumentEmbeddingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        document_chunk_id,
        embedding_model: str,
        vector: list[float],
        metadata: dict | None = None,
    ):
        row = DocumentEmbedding(
            document_chunk_id=document_chunk_id,
            embedding_model=embedding_model,
            embedding_json=json.dumps(vector),
            embedding_vector=vector,
            metadata_json=json.dumps(metadata or {}),
        )

        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        return row

    def list_for_chunk(self, chunk_id):
        result = self.db.execute(
            select(DocumentEmbedding).where(
                DocumentEmbedding.document_chunk_id == chunk_id
            )
        )

        return list(result.scalars().all())
