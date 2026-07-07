from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.entities import get_db
from app.schemas.entity_tag import EntityTagCreate, EntityTagResponse
from app.services.entity_tag_service import EntityTagService

router = APIRouter(tags=["Entity Tags"])


@router.post("/api/v1/entity-tags", response_model=EntityTagResponse, status_code=status.HTTP_201_CREATED)
def attach_tag_to_entity(data: EntityTagCreate, db: Session = Depends(get_db)):
    return EntityTagService(db).attach_tag(data)


@router.get("/api/v1/entities/{entity_id}/tags", response_model=list[EntityTagResponse])
def list_entity_tags(entity_id: UUID, db: Session = Depends(get_db)):
    return EntityTagService(db).list_entity_tags(entity_id)
