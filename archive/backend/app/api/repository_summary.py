from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_summary import (
    RepositorySummary,
    RepositorySummaryBuilder,
    RepositorySummarySection,
)
from app.connectors.repository.repository_summary_summary import RepositorySummarySummaryBuilder
from app.schemas.repository_summary import (
    RepositorySummaryRequest,
    RepositorySummaryResponse,
    RepositorySummarySectionResponse,
    RepositorySummarySummaryResponse,
)

router = APIRouter()


def serialize_repository_summary_section(section: RepositorySummarySection) -> RepositorySummarySectionResponse:
    return RepositorySummarySectionResponse(name=section.name, value=section.value)


def serialize_repository_summary(summary: RepositorySummary) -> RepositorySummaryResponse:
    summary_status = RepositorySummarySummaryBuilder().build(summary)

    return RepositorySummaryResponse(
        repository_path=summary.repository_path,
        title=summary.title,
        sections=[serialize_repository_summary_section(section) for section in summary.sections],
        section_count=summary.section_count,
        section_names=summary.section_names,
        summary=RepositorySummarySummaryResponse(
            outcome=summary_status.outcome,
            message=summary_status.message,
            action_required=summary_status.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-summary",
    response_model=RepositorySummaryResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_summary(data: RepositorySummaryRequest):
    try:
        summary = RepositorySummaryBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )
        return serialize_repository_summary(summary)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
