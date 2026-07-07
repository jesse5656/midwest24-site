from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.ai.mock_embedding_provider import MockEmbeddingProvider
from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.processing.chunker import Chunker
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_embedding_repository import DocumentEmbeddingRepository
from app.repositories.document_text_repository import DocumentTextRepository


def utc_now():
    return datetime.now(UTC)


class DocumentWorker:
    def __init__(self, db: Session):
        self.db = db
        self.text_repository = DocumentTextRepository(db)
        self.chunk_repository = DocumentChunkRepository(db)
        self.embedding_repository = DocumentEmbeddingRepository(db)
        self.embedding_provider = MockEmbeddingProvider()
        self.chunker = Chunker()

    def process(self, job: ProcessingJob):
        job.status = "running"
        job.started_at = utc_now()
        job.progress = 10
        self.db.commit()

        document = self.db.get(Document, job.document_id)
        extracted_text = ""

        if document:
            path = Path(document.storage_path)

            if path.exists() and path.suffix.lower() in (".txt", ".md"):
                extracted_text = path.read_text(errors="ignore")

        if extracted_text:
            text_row = self.text_repository.create(document.id, extracted_text)
            chunks = self.chunker.chunk(extracted_text)

            for index, chunk in enumerate(chunks):
                chunk_row = self.chunk_repository.create(
                    document_text_id=text_row.id,
                    chunk_index=index,
                    text=chunk,
                )

                vector = self.embedding_provider.embed(chunk)

                self.embedding_repository.create(
                    document_chunk_id=chunk_row.id,
                    embedding_model="mock",
                    vector=vector,
                )

        job.status = "completed"
        job.progress = 100
        job.completed_at = utc_now()
        self.db.commit()

        return job
