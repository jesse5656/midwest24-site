from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.context import get_db
from app.connectors.repository import RepositoryIncrementalIngestor, RepositoryManifestStore
from app.schemas.repository_incremental_ingestion import (
    RepositoryChangeSetResponse,
    RepositoryIncrementalIngestionCreate,
    RepositoryIncrementalIngestionResponse,
)
from app.schemas.repository_ingestion import (
    ProcessingJobStatusCountsResponse,
    RepositoryDuplicateFileResponse,
    RepositoryIngestionFailureResponse,
    RepositoryIngestionResponse,
    RepositorySkippedPathResponse,
    RepositoryUnsupportedFileResponse,
)

router = APIRouter()


def serialize_ingestion_report(report):
    if report is None:
        return None

    return RepositoryIngestionResponse(
        discovered_count=report.discovered_count,
        document_count=report.document_count,
        processing_job_count=report.processing_job_count,
        bytes_ingested=report.bytes_ingested,
        elapsed_ms=report.elapsed_ms,
        skipped_count=report.skipped_count,
        unsupported_count=report.unsupported_count,
        duplicate_count=report.duplicate_count,
        failures=[
            RepositoryIngestionFailureResponse(path=item.path, reason=item.reason)
            for item in report.failures
        ],
        skipped_paths=[
            RepositorySkippedPathResponse(path=item.path, reason=item.reason)
            for item in report.skipped_paths
        ],
        unsupported_files=[
            RepositoryUnsupportedFileResponse(
                path=item.path,
                suffix=item.suffix,
                reason=item.reason,
            )
            for item in report.unsupported_files
        ],
        duplicate_files=[
            RepositoryDuplicateFileResponse(path=item.path, reason=item.reason)
            for item in report.duplicate_files
        ],
        processing_jobs_by_status=ProcessingJobStatusCountsResponse(
            pending=report.processing_jobs_by_status.pending,
            running=report.processing_jobs_by_status.running,
            completed=report.processing_jobs_by_status.completed,
            failed=report.processing_jobs_by_status.failed,
            total=report.processing_jobs_by_status.total,
        ),
    )


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
            ingestion_report=serialize_ingestion_report(result.ingestion_report),
            new_count=result.new_count,
            modified_count=result.modified_count,
            deleted_count=result.deleted_count,
            unchanged_count=result.unchanged_count,
            changed_count=result.changed_count,
            ingested_document_count=result.ingested_document_count,
            processing_job_count=result.processing_job_count,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
