from fastapi import APIRouter, HTTPException, status

from app.connectors.repository import (
    GitCommitFileChangeSet,
    GitFileChange,
    GitFileChangePreview,
    GitFileChangePreviewBuilder,
    GitFileChangeSummaryBuilder,
)
from app.schemas.git_file_change_preview import (
    GitCommitFileChangeSetResponse,
    GitFileChangeOperatorSummaryResponse,
    GitFileChangePreviewRequest,
    GitFileChangePreviewResponse,
    GitFileChangeResponse,
)

router = APIRouter()


def serialize_git_file_change(change: GitFileChange) -> GitFileChangeResponse:
    return GitFileChangeResponse(
        status=change.status,
        path=change.path,
        is_added=change.is_added,
        is_modified=change.is_modified,
        is_deleted=change.is_deleted,
        is_renamed=change.is_renamed,
    )


def serialize_git_commit_file_change_set(
    commit: GitCommitFileChangeSet,
) -> GitCommitFileChangeSetResponse:
    return GitCommitFileChangeSetResponse(
        commit_sha=commit.commit_sha,
        short_sha=commit.short_sha,
        subject=commit.subject,
        files=[serialize_git_file_change(file) for file in commit.files],
        file_count=commit.file_count,
        added_count=commit.added_count,
        modified_count=commit.modified_count,
        deleted_count=commit.deleted_count,
        renamed_count=commit.renamed_count,
    )


def serialize_git_file_change_preview(preview: GitFileChangePreview) -> GitFileChangePreviewResponse:
    summary = GitFileChangeSummaryBuilder().build(preview)

    return GitFileChangePreviewResponse(
        commit_count=preview.commit_count,
        file_change_count=preview.file_change_count,
        added_count=preview.added_count,
        modified_count=preview.modified_count,
        deleted_count=preview.deleted_count,
        renamed_count=preview.renamed_count,
        touched_paths=preview.touched_paths,
        commits=[
            serialize_git_commit_file_change_set(commit)
            for commit in preview.commits
        ],
        summary=GitFileChangeOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-git-file-change-preview",
    response_model=GitFileChangePreviewResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_git_file_change_preview(data: GitFileChangePreviewRequest):
    try:
        preview = GitFileChangePreviewBuilder().build(
            repository_path=data.repository_path,
            limit=data.limit,
        )
        return serialize_git_file_change_preview(preview)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
