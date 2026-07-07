from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.processing_job import ProcessingJob
from app.schemas.processing_job import ProcessingJobCreate


class ProcessingJobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ProcessingJobCreate) -> ProcessingJob:
        job = ProcessingJob(**data.model_dump())
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def list_all(self) -> list[ProcessingJob]:
        result = self.db.execute(select(ProcessingJob).order_by(ProcessingJob.created_at.desc()))
        return list(result.scalars().all())

    def list_for_document(self, document_id: UUID) -> list[ProcessingJob]:
        result = self.db.execute(
            select(ProcessingJob)
            .where(ProcessingJob.document_id == document_id)
            .order_by(ProcessingJob.created_at.desc())
        )
        return list(result.scalars().all())
