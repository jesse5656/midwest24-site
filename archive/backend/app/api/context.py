from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.entities import get_db
from app.schemas.context import EntityContextResponse
from app.services.context_service import ContextService

router = APIRouter(prefix="/api/v1/context", tags=["Context"])


@router.get(
    "/{entity_id}",
    response_model=EntityContextResponse,
)
def get_entity_context(
    entity_id: UUID,
    db: Session = Depends(get_db),
):
    return ContextService(db).get_context(entity_id)
