from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.entities import get_db
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter(tags=["Documents"])


@router.post("/api/v1/entities/{entity_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(entity_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return DocumentService(db).upload_document(entity_id, file)


@router.get("/api/v1/entities/{entity_id}/documents", response_model=list[DocumentResponse])
def list_entity_documents(entity_id: UUID, db: Session = Depends(get_db)):
    return DocumentService(db).list_entity_documents(entity_id)
