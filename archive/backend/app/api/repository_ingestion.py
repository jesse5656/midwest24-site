from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.connectors.repository import ArchiveRepositoryIngestor
from app.api.context import get_db
from app.connectors.repository.operator_summary import RepositoryIngestionSummaryBuilder
from app.schemas.repository_ingestion import (
    ProcessingJobStatusCountsResponse,
    RepositoryDuplicateFileResponse,
    RepositoryIngestionCreate,
    RepositoryIngestionFailureResponse,
    RepositoryIngestionResponse,
    RepositorySkippedPathResponse,
    RepositoryUnsupportedFileResponse,
)
from app.schemas.repository_operator_summary import RepositoryIngestionOperatorSummaryResponse

router = APIRouter()


def serialize_repository_ingestion_report(report):
    summary = RepositoryIngestionSummaryBuilder().build(report)

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
        summary=RepositoryIngestionOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
            has_failures=summary.has_failures,
            has_duplicates=summary.has_duplicates,
            has_unsupported_files=summary.has_unsupported_files,
            has_skipped_paths=summary.has_skipped_paths,
        ),
    )


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
        report = ArchiveRepositoryIngestor(db).ingest_repository(
            entity_id=data.entity_id,
            repository_path=data.repository_path,
        )
        return serialize_repository_ingestion_report(report)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
