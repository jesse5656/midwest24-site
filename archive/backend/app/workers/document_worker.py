from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.processing.chunker import Chunker
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_text_repository import DocumentTextRepository


def utc_now():
    return datetime.now(UTC)


class DocumentWorker:
    def __init__(self, db: Session):
        self.db = db
        self.text_repository = DocumentTextRepository(db)
        self.chunk_repository = DocumentChunkRepository(db)
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
            text_row = self.text_repository.create(
                document.id,
                extracted_text,
            )

            chunks = self.chunker.chunk(extracted_text)

            for i, chunk in enumerate(chunks):
                self.chunk_repository.create(
                    document_text_id=text_row.id,
                    chunk_index=i,
                    text=chunk,
                )

        job.status = "completed"
        job.progress = 100
        job.completed_at = utc_now()

        self.db.commit()

        return job
