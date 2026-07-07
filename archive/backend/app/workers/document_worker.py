from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.repositories.document_text_repository import DocumentTextRepository


def utc_now():
    return datetime.now(UTC)


class DocumentWorker:
    def __init__(self, db: Session):
        self.db = db
        self.document_text_repository = DocumentTextRepository(db)

    def process(self, job: ProcessingJob):
        job.status = "running"
        job.started_at = utc_now()
        job.progress = 10

        self.db.commit()

        document = self.db.get(Document, job.document_id)

        text = ""

        if document is not None:
            path = Path(document.storage_path)

            if path.exists():
                suffix = path.suffix.lower()

                if suffix in (".txt", ".md"):
                    text = path.read_text(errors="ignore")

        if text:
            self.document_text_repository.create(
                document.id,
                text,
            )

        job.status = "completed"
        job.progress = 100
        job.completed_at = utc_now()

        self.db.commit()

        return job
