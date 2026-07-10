from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_intelligence_report import (
    RepositoryIntelligenceReport,
    RepositoryIntelligenceReportBuilder,
    RepositoryIntelligenceReportSection,
)
from app.connectors.repository.repository_intelligence_report_summary import (
    RepositoryIntelligenceReportSummaryBuilder,
)
from app.schemas.repository_intelligence_report import (
    RepositoryIntelligenceReportRequest,
    RepositoryIntelligenceReportResponse,
    RepositoryIntelligenceReportSectionResponse,
    RepositoryIntelligenceReportSummaryResponse,
)

router = APIRouter()


def serialize_repository_intelligence_report_section(
    section: RepositoryIntelligenceReportSection,
) -> RepositoryIntelligenceReportSectionResponse:
    return RepositoryIntelligenceReportSectionResponse(
        name=section.name,
        content=section.content,
        status=section.status,
    )


def serialize_repository_intelligence_report(
    report: RepositoryIntelligenceReport,
) -> RepositoryIntelligenceReportResponse:
    summary = RepositoryIntelligenceReportSummaryBuilder().build(
        report
    )

    return RepositoryIntelligenceReportResponse(
        repository_path=report.repository_path,
        repository_name=report.repository_name,
        title=report.title,
        sections=[
            serialize_repository_intelligence_report_section(
                section
            )
            for section in report.sections
        ],
        section_count=report.section_count,
        section_names=report.section_names,
        info_count=report.info_count,
        warning_count=report.warning_count,
        critical_count=report.critical_count,
        is_healthy=report.is_healthy,
        markdown=report.as_markdown(),
        summary=RepositoryIntelligenceReportSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-intelligence-report",
    response_model=RepositoryIntelligenceReportResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_intelligence_report(
    data: RepositoryIntelligenceReportRequest,
):
    try:
        report = RepositoryIntelligenceReportBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )

        return serialize_repository_intelligence_report(
            report
        )

    except (FileNotFoundError, NotADirectoryError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
