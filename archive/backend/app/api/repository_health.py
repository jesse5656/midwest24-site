from fastapi import APIRouter, status

from app.connectors.repository import (
    ArchiveBackendHealthEvaluator,
    ArchiveBackendHealthInputs,
    RepositoryHealthReport,
    RepositoryHealthSummaryBuilder,
)
from app.schemas.repository_health import (
    ArchiveBackendHealthRequest,
    RepositoryHealthCheckResponse,
    RepositoryHealthOperatorSummaryResponse,
    RepositoryHealthReportResponse,
)

router = APIRouter()


def serialize_repository_health_report(report: RepositoryHealthReport) -> RepositoryHealthReportResponse:
    summary = RepositoryHealthSummaryBuilder().build(report)

    return RepositoryHealthReportResponse(
        name=report.name,
        checks=[
            RepositoryHealthCheckResponse(
                name=check.name,
                passed=check.passed,
                message=check.message,
                severity=check.severity,
            )
            for check in report.checks
        ],
        passed=report.passed,
        check_count=report.check_count,
        passed_count=report.passed_count,
        failed_count=report.failed_count,
        warning_count=report.warning_count,
        error_count=report.error_count,
        summary=RepositoryHealthOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/archive-backend-health",
    response_model=RepositoryHealthReportResponse,
    status_code=status.HTTP_200_OK,
)
def get_archive_backend_health(data: ArchiveBackendHealthRequest):
    report = ArchiveBackendHealthEvaluator().evaluate(
        ArchiveBackendHealthInputs(
            test_count=data.test_count,
            has_progress_ledger=data.has_progress_ledger,
            has_operating_plan=data.has_operating_plan,
            has_runbook=data.has_runbook,
            has_git_intelligence=data.has_git_intelligence,
            has_code_intelligence=data.has_code_intelligence,
        )
    )

    return serialize_repository_health_report(report)
