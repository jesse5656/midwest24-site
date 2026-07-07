from sqlalchemy.orm import Session

from app.models.processing_job import ProcessingJob


class DocumentWorker:
    def __init__(self, db: Session):
        self.db = db

    def process(self, job: ProcessingJob):
        """
        Placeholder worker.

        Future versions will:

        - extract PDF text
        - OCR images
        - parse DOCX
        - generate embeddings

        For now it simply marks the job complete.
        """

        job.status = "completed"
        job.progress = 100

        self.db.commit()
        self.db.refresh(job)

        return job
