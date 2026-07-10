from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_drift_detection import (
    RepositoryDriftDetector,
    RepositoryDriftFinding,
    RepositoryDriftReport,
)
from app.connectors.repository.repository_drift_detection_summary import (
    RepositoryDriftSummaryBuilder,
)
from app.schemas.repository_drift_detection import (
    RepositoryDriftDetectionRequest,
    RepositoryDriftDetectionResponse,
    RepositoryDriftFindingResponse,
    RepositoryDriftSummaryResponse,
)

router = APIRouter()


def serialize_repository_drift_finding(
    finding: RepositoryDriftFinding,
) -> RepositoryDriftFindingResponse:
    return RepositoryDriftFindingResponse(
        finding_type=finding.finding_type,
        severity=finding.severity,
        subject=finding.subject,
        message=finding.message,
    )


def serialize_repository_drift_report(
    report: RepositoryDriftReport,
) -> RepositoryDriftDetectionResponse:
    summary = RepositoryDriftSummaryBuilder().build(report)

    return RepositoryDriftDetectionResponse(
        baseline_repository_path=report.baseline_repository_path,
        candidate_repository_path=report.candidate_repository_path,
        findings=[
            serialize_repository_drift_finding(finding)
            for finding in report.findings
        ],
        finding_count=report.finding_count,
        has_drift=report.has_drift,
        added_count=report.added_count,
        removed_count=report.removed_count,
        warning_count=report.warning_count,
        critical_count=report.critical_count,
        finding_types=report.finding_types,
        severity_levels=report.severity_levels,
        summary=RepositoryDriftSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-drift-detection",
    response_model=RepositoryDriftDetectionResponse,
    status_code=status.HTTP_200_OK,
)
def detect_repository_drift(
    data: RepositoryDriftDetectionRequest,
):
    try:
        report = RepositoryDriftDetector().compare(
            baseline_repository_path=data.baseline_repository_path,
            candidate_repository_path=data.candidate_repository_path,
            max_depth=data.max_depth,
        )
        return serialize_repository_drift_report(report)

    except (FileNotFoundError, NotADirectoryError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
