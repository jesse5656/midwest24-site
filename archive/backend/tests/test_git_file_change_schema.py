import pytest
from pydantic import ValidationError

from app.schemas.git_file_change_preview import (
    GitCommitFileChangeSetResponse,
    GitFileChangeOperatorSummaryResponse,
    GitFileChangePreviewRequest,
    GitFileChangePreviewResponse,
    GitFileChangeResponse,
)


def make_file_response(path="README.md"):
    return GitFileChangeResponse(
        status="M",
        path=path,
        is_added=False,
        is_modified=True,
        is_deleted=False,
        is_renamed=False,
    )


def test_file_change_preview_request_defaults_limit():
    request = GitFileChangePreviewRequest(repository_path="/repo")

    assert request.limit == 10


def test_file_change_preview_request_rejects_empty_path():
    with pytest.raises(ValidationError):
        GitFileChangePreviewRequest(repository_path="")


def test_file_change_preview_request_rejects_zero_limit():
    with pytest.raises(ValidationError):
        GitFileChangePreviewRequest(repository_path="/repo", limit=0)


def test_file_change_preview_request_rejects_limit_over_100():
    with pytest.raises(ValidationError):
        GitFileChangePreviewRequest(repository_path="/repo", limit=101)


def test_file_change_response_accepts_payload():
    response = make_file_response()

    assert response.path == "README.md"
    assert response.is_modified is True


def test_commit_file_change_set_response_accepts_payload():
    response = GitCommitFileChangeSetResponse(
        commit_sha="abcdef",
        short_sha="abc",
        subject="Subject",
        files=[make_file_response()],
        file_count=1,
        added_count=0,
        modified_count=1,
        deleted_count=0,
        renamed_count=0,
    )

    assert response.file_count == 1
    assert response.files[0].path == "README.md"


def test_file_change_preview_response_serializes_nested_payload():
    file_response = make_file_response()
    commit_response = GitCommitFileChangeSetResponse(
        commit_sha="abcdef",
        short_sha="abc",
        subject="Subject",
        files=[file_response],
        file_count=1,
        added_count=0,
        modified_count=1,
        deleted_count=0,
        renamed_count=0,
    )

    response = GitFileChangePreviewResponse(
        commit_count=1,
        file_change_count=1,
        added_count=0,
        modified_count=1,
        deleted_count=0,
        renamed_count=0,
        touched_paths=["README.md"],
        commits=[commit_response],
        summary=GitFileChangeOperatorSummaryResponse(
            outcome="file_changes_found",
            message="ok",
            action_required=False,
        ),
    )

    payload = response.model_dump()

    assert payload["commits"][0]["files"][0]["path"] == "README.md"
    assert payload["summary"]["outcome"] == "file_changes_found"
