from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.context import get_db
from app.api.repository_ingestion import serialize_repository_ingestion_report
from app.connectors.repository import RepositoryIncrementalIngestor, RepositoryManifestStore
from app.connectors.repository.operator_summary import RepositoryIncrementalSummaryBuilder
from app.schemas.repository_incremental_ingestion import (
    RepositoryChangeSetResponse,
    RepositoryIncrementalIngestionCreate,
    RepositoryIncrementalIngestionResponse,
)
from app.schemas.repository_operator_summary import RepositoryIncrementalOperatorSummaryResponse

router = APIRouter()


@router.post(
    "/api/v1/repository-incremental-ingestions",
    response_model=RepositoryIncrementalIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repository_incremental_ingestion(
    data: RepositoryIncrementalIngestionCreate,
    db: Session = Depends(get_db),
):
    try:
        result = RepositoryIncrementalIngestor(
            db=db,
            manifest_store=RepositoryManifestStore(data.manifest_path),
        ).ingest_changed_repository(
            entity_id=data.entity_id,
            repository_path=data.repository_path,
        )

        summary = RepositoryIncrementalSummaryBuilder().build(result)

        return RepositoryIncrementalIngestionResponse(
            changes=RepositoryChangeSetResponse(
                new_files=result.changes.new_files,
                modified_files=result.changes.modified_files,
                deleted_files=result.changes.deleted_files,
                unchanged_files=result.changes.unchanged_files,
                changed_files=result.changes.changed_files,
                changed_count=result.changes.changed_count,
            ),
            manifest_updated=result.manifest_updated,
            ingestion_report=serialize_repository_ingestion_report(result.ingestion_report)
            if result.ingestion_report
            else None,
            new_count=result.new_count,
            modified_count=result.modified_count,
            deleted_count=result.deleted_count,
            unchanged_count=result.unchanged_count,
            changed_count=result.changed_count,
            ingested_document_count=result.ingested_document_count,
            processing_job_count=result.processing_job_count,
            summary=RepositoryIncrementalOperatorSummaryResponse(
                outcome=summary.outcome,
                message=summary.message,
                action_required=summary.action_required,
                changed_count=summary.changed_count,
                ingested_document_count=summary.ingested_document_count,
            ),
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
