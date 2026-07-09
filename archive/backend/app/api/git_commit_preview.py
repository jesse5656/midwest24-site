from fastapi import APIRouter, HTTPException, status

from app.connectors.repository import (
    GitCommit,
    GitCommitPreview,
    GitCommitPreviewBuilder,
    GitCommitPreviewSummaryBuilder,
)
from app.schemas.git_commit_preview import (
    GitAuthorContributionResponse,
    GitCommitPreviewOperatorSummaryResponse,
    GitCommitPreviewRequest,
    GitCommitPreviewResponse,
    GitCommitResponse,
)

router = APIRouter()


def serialize_git_commit(commit: GitCommit | None):
    if commit is None:
        return None

    return GitCommitResponse(
        sha=commit.sha,
        short_sha=commit.short_sha,
        author_name=commit.author_name,
        author_email=commit.author_email,
        authored_at=commit.authored_at,
        subject=commit.subject,
        display=commit.display,
    )


def serialize_git_commit_preview(preview: GitCommitPreview) -> GitCommitPreviewResponse:
    summary = GitCommitPreviewSummaryBuilder().build(preview)

    return GitCommitPreviewResponse(
        commit_count=preview.commit_count,
        commits=[serialize_git_commit(commit) for commit in preview.commits],
        authors=[
            GitAuthorContributionResponse(
                author_name=author.author_name,
                author_email=author.author_email,
                commit_count=author.commit_count,
            )
            for author in preview.authors
        ],
        latest_commit=serialize_git_commit(preview.latest_commit),
        oldest_commit=serialize_git_commit(preview.oldest_commit),
        summary=GitCommitPreviewOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-git-commit-preview",
    response_model=GitCommitPreviewResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_git_commit_preview(data: GitCommitPreviewRequest):
    try:
        preview = GitCommitPreviewBuilder().build(
            repository_path=data.repository_path,
            limit=data.limit,
        )
        return serialize_git_commit_preview(preview)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
