from fastapi import APIRouter, HTTPException, status

from app.connectors.repository import (
    GitRepositoryOperatorSummaryBuilder,
    GitRepositorySummary,
    GitRepositorySummaryBuilder,
)
from app.schemas.git_repository_intelligence import (
    GitRepositoryIntelligenceEnvelopeResponse,
    GitRepositoryIntelligenceRequest,
    GitRepositoryIntelligenceResponse,
    GitRepositoryOperatorSummaryResponse,
)

router = APIRouter()


def serialize_git_repository_summary(summary: GitRepositorySummary) -> GitRepositoryIntelligenceResponse:
    return GitRepositoryIntelligenceResponse(
        is_repository=summary.is_repository,
        root=summary.root,
        current_branch=summary.current_branch,
        recent_commit_count=summary.recent_commit_count,
        is_clean=summary.is_clean,
    )


def serialize_git_operator_summary(summary: GitRepositorySummary) -> GitRepositoryOperatorSummaryResponse:
    operator_summary = GitRepositoryOperatorSummaryBuilder().build(summary)

    return GitRepositoryOperatorSummaryResponse(
        outcome=operator_summary.outcome,
        message=operator_summary.message,
        action_required=operator_summary.action_required,
    )


@router.post(
    "/api/v1/repository-git-intelligence",
    response_model=GitRepositoryIntelligenceEnvelopeResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_git_intelligence(
    data: GitRepositoryIntelligenceRequest,
):
    try:
        summary = GitRepositorySummaryBuilder().build(
            repository_path=data.repository_path,
            commit_limit=data.commit_limit,
        )

        return GitRepositoryIntelligenceEnvelopeResponse(
            intelligence=serialize_git_repository_summary(summary),
            summary=serialize_git_operator_summary(summary),
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
