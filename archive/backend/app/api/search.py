from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.entities import get_db
from app.schemas.entity import EntityResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/api/v1/search", tags=["Search"])


@router.get("/entities", response_model=list[EntityResponse])
def search_entities(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    return SearchService(db).search_entities(q)
