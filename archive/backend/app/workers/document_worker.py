from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.processing_job import ProcessingJob


def utc_now() -> datetime:
    return datetime.now(UTC)


class DocumentWorker:
    def __init__(self, db: Session):
        self.db = db

    def process(self, job: ProcessingJob):
        """
        Placeholder document worker.

        Future versions will extract text, OCR images, parse DOCX/PDF files,
        generate chunks, and prepare embeddings.

        For now it records a proper lifecycle:
        pending -> running -> completed.
        """

        job.status = "running"
        job.started_at = utc_now()
        job.progress = 10
        self.db.commit()
        self.db.refresh(job)

        job.status = "completed"
        job.completed_at = utc_now()
        job.progress = 100
        self.db.commit()
        self.db.refresh(job)

        return job
