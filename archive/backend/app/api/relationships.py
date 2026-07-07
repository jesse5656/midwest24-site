from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.entities import get_db
from app.schemas.relationship import RelationshipCreate, RelationshipResponse
from app.services.relationship_service import RelationshipService

router = APIRouter(tags=["Relationships"])


@router.post("/api/v1/relationships", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED)
def create_relationship(data: RelationshipCreate, db: Session = Depends(get_db)):
    return RelationshipService(db).create_relationship(data)


@router.get("/api/v1/relationships", response_model=list[RelationshipResponse])
def list_relationships(db: Session = Depends(get_db)):
    return RelationshipService(db).list_relationships()


@router.get("/api/v1/entities/{entity_id}/relationships", response_model=list[RelationshipResponse])
def list_entity_relationships(entity_id: UUID, db: Session = Depends(get_db)):
    return RelationshipService(db).list_entity_relationships(entity_id)
