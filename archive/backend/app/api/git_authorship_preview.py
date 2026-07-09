from fastapi import APIRouter, HTTPException, status

from app.connectors.repository import (
    GitAuthorSummary,
    GitAuthorshipPreview,
    GitAuthorshipPreviewBuilder,
    GitAuthorshipSummaryBuilder,
)
from app.schemas.git_authorship_preview import (
    GitAuthorSummaryResponse,
    GitAuthorshipOperatorSummaryResponse,
    GitAuthorshipPreviewRequest,
    GitAuthorshipPreviewResponse,
)

router = APIRouter()


def serialize_git_author_summary(author: GitAuthorSummary | None):
    if author is None:
        return None

    return GitAuthorSummaryResponse(
        author_name=author.author_name,
        author_email=author.author_email,
        commit_count=author.commit_count,
        first_authored_at=author.first_authored_at,
        last_authored_at=author.last_authored_at,
        identity=author.identity,
    )


def serialize_git_authorship_preview(preview: GitAuthorshipPreview) -> GitAuthorshipPreviewResponse:
    summary = GitAuthorshipSummaryBuilder().build(preview)

    return GitAuthorshipPreviewResponse(
        commit_count=preview.commit_count,
        author_count=preview.author_count,
        authors=[serialize_git_author_summary(author) for author in preview.authors],
        top_author=serialize_git_author_summary(preview.top_author),
        first_authored_at=preview.first_authored_at,
        last_authored_at=preview.last_authored_at,
        summary=GitAuthorshipOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-git-authorship-preview",
    response_model=GitAuthorshipPreviewResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_git_authorship_preview(data: GitAuthorshipPreviewRequest):
    try:
        preview = GitAuthorshipPreviewBuilder().build(
            repository_path=data.repository_path,
            limit=data.limit,
        )
        return serialize_git_authorship_preview(preview)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
