from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.entities import get_db
from app.schemas.tag import TagCreate, TagResponse
from app.services.tag_service import TagService

router = APIRouter(prefix="/api/v1/tags", tags=["Tags"])


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(data: TagCreate, db: Session = Depends(get_db)):
    return TagService(db).create_tag(data)


@router.get("", response_model=list[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    return TagService(db).list_tags()
