from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings

from app.repositories.document_repository import DocumentRepository
from app.repositories.entity_repository import EntityRepository


STORAGE_ROOT = Path(settings.document_storage_root)


class DocumentService:
    def __init__(self, db: Session):
        self.entity_repository = EntityRepository(db)
        self.document_repository = DocumentRepository(db)

    def upload_document(self, entity_id: UUID, file: UploadFile):
        if self.entity_repository.get(entity_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

        STORAGE_ROOT.mkdir(parents=True, exist_ok=True)

        safe_name = file.filename or "uploaded-file"
        storage_name = f"{uuid4()}-{safe_name}"
        storage_path = STORAGE_ROOT / storage_name

        with storage_path.open("wb") as output:
            output.write(file.file.read())

        return self.document_repository.create(
            entity_id=entity_id,
            filename=safe_name,
            mime_type=file.content_type,
            storage_path=str(storage_path),
        )

    def list_entity_documents(self, entity_id: UUID):
        if self.entity_repository.get(entity_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

        return self.document_repository.list_for_entity(entity_id)
