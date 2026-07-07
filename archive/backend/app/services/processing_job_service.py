from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.schemas.processing_job import ProcessingJobCreate


class ProcessingJobService:
    def __init__(self, db: Session):
        self.document_repository = DocumentRepository(db)
        self.processing_job_repository = ProcessingJobRepository(db)

    def create_job(self, data: ProcessingJobCreate):
        if self.document_repository.get(data.document_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        return self.processing_job_repository.create(data)

    def list_jobs(self):
        return self.processing_job_repository.list_all()

    def list_document_jobs(self, document_id: UUID):
        if self.document_repository.get(document_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        return self.processing_job_repository.list_for_document(document_id)
