from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_embedding import DocumentEmbedding
from app.models.document_text import DocumentText
from app.models.entity import Entity


class SemanticSearchRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_chunks(self, query_vector: list[float], limit: int = 10):
        distance = DocumentEmbedding.embedding_vector.cosine_distance(query_vector).label("distance")

        result = self.db.execute(
            select(DocumentChunk, DocumentEmbedding, DocumentText, Document, Entity, distance)
            .join(DocumentEmbedding, DocumentEmbedding.document_chunk_id == DocumentChunk.id)
            .join(DocumentText, DocumentText.id == DocumentChunk.document_text_id)
            .join(Document, Document.id == DocumentText.document_id)
            .join(Entity, Entity.id == Document.entity_id)
            .where(DocumentEmbedding.embedding_vector.is_not(None))
            .order_by(distance.asc())
            .limit(limit)
        )

        return result.all()
