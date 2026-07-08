from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.entities import get_db
from app.schemas.semantic_search import SemanticSearchRequest, SemanticSearchResult
from app.services.semantic_search_service import SemanticSearchService

router = APIRouter(tags=["Semantic Search"])


@router.post("/api/v1/search/semantic", response_model=list[SemanticSearchResult])
def semantic_search(request: SemanticSearchRequest, db: Session = Depends(get_db)):
    rows = SemanticSearchService(db).search(request.query, request.limit)

    return [
        SemanticSearchResult(
            chunk_id=str(chunk.id),
            text=chunk.text,
            distance=float(distance),
        )
        for chunk, embedding, distance in rows
    ]
