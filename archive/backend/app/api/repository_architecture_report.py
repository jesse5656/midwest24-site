from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_architecture_report import (
    RepositoryArchitectureFinding,
    RepositoryArchitectureReport,
    RepositoryArchitectureReportBuilder,
)
from app.connectors.repository.repository_architecture_report_summary import (
    RepositoryArchitectureReportSummaryBuilder,
)
from app.schemas.repository_architecture_report import (
    RepositoryArchitectureFindingResponse,
    RepositoryArchitectureReportRequest,
    RepositoryArchitectureReportResponse,
    RepositoryArchitectureReportSummaryResponse,
)

router = APIRouter()


def serialize_repository_architecture_finding(
    finding: RepositoryArchitectureFinding,
) -> RepositoryArchitectureFindingResponse:
    return RepositoryArchitectureFindingResponse(
        name=finding.name,
        severity=finding.severity,
        message=finding.message,
    )


def serialize_repository_architecture_report(
    report: RepositoryArchitectureReport,
) -> RepositoryArchitectureReportResponse:
    summary = RepositoryArchitectureReportSummaryBuilder().build(report)

    return RepositoryArchitectureReportResponse(
        repository_path=report.repository_path,
        title=report.title,
        findings=[
            serialize_repository_architecture_finding(finding)
            for finding in report.findings
        ],
        finding_count=report.finding_count,
        severity_levels=report.severity_levels,
        info_count=report.info_count,
        warning_count=report.warning_count,
        critical_count=report.critical_count,
        has_warnings=report.has_warnings,
        summary=RepositoryArchitectureReportSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-architecture-report",
    response_model=RepositoryArchitectureReportResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_architecture_report(data: RepositoryArchitectureReportRequest):
    try:
        report = RepositoryArchitectureReportBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )
        return serialize_repository_architecture_report(report)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
