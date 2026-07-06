from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.entity import EntityCreate, EntityResponse, EntityUpdate
from app.services.entity_service import EntityService

router = APIRouter(prefix="/api/v1/entities", tags=["Entities"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(data: EntityCreate, db: Session = Depends(get_db)):
    return EntityService(db).create_entity(data)


@router.get("", response_model=list[EntityResponse])
def list_entities(db: Session = Depends(get_db)):
    return EntityService(db).list_entities()


@router.get("/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: UUID, db: Session = Depends(get_db)):
    return EntityService(db).get_entity(entity_id)


@router.patch("/{entity_id}", response_model=EntityResponse)
def update_entity(entity_id: UUID, data: EntityUpdate, db: Session = Depends(get_db)):
    return EntityService(db).update_entity(entity_id, data)


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entity(entity_id: UUID, db: Session = Depends(get_db)):
    EntityService(db).delete_entity(entity_id)
    return None
