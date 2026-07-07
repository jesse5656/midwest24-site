from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.entities import get_db
from app.schemas.processing_job import ProcessingJobCreate, ProcessingJobResponse
from app.services.processing_job_service import ProcessingJobService

router = APIRouter(tags=["Processing Jobs"])


@router.post("/api/v1/processing-jobs", response_model=ProcessingJobResponse, status_code=status.HTTP_201_CREATED)
def create_processing_job(data: ProcessingJobCreate, db: Session = Depends(get_db)):
    return ProcessingJobService(db).create_job(data)


@router.get("/api/v1/processing-jobs", response_model=list[ProcessingJobResponse])
def list_processing_jobs(db: Session = Depends(get_db)):
    return ProcessingJobService(db).list_jobs()


@router.get("/api/v1/documents/{document_id}/processing-jobs", response_model=list[ProcessingJobResponse])
def list_document_processing_jobs(document_id: UUID, db: Session = Depends(get_db)):
    return ProcessingJobService(db).list_document_jobs(document_id)
