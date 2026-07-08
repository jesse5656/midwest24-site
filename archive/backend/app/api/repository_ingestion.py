from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.connectors.repository import ArchiveRepositoryIngestor
from app.api.context import get_db
from app.schemas.repository_ingestion import (
    RepositoryIngestionCreate,
    RepositoryIngestionResponse,
)

router = APIRouter()


@router.post(
    "/api/v1/repository-ingestions",
    response_model=RepositoryIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repository_ingestion(
    data: RepositoryIngestionCreate,
    db: Session = Depends(get_db),
):
    try:
        return ArchiveRepositoryIngestor(db).ingest_repository(
            entity_id=data.entity_id,
            repository_path=data.repository_path,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
