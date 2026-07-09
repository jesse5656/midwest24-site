import pytest
from pydantic import ValidationError

from app.schemas.git_commit_preview import (
    GitAuthorContributionResponse,
    GitCommitPreviewOperatorSummaryResponse,
    GitCommitPreviewRequest,
    GitCommitPreviewResponse,
    GitCommitResponse,
)


def make_commit_response(subject="Subject"):
    return GitCommitResponse(
        sha="abcdef",
        short_sha="abc",
        author_name="A",
        author_email="a@example.com",
        authored_at="2026-01-01T00:00:00Z",
        subject=subject,
        display=f"abc {subject}",
    )


def test_git_commit_preview_request_defaults_limit():
    request = GitCommitPreviewRequest(repository_path="/repo")

    assert request.limit == 10


def test_git_commit_preview_request_accepts_limit():
    request = GitCommitPreviewRequest(repository_path="/repo", limit=25)

    assert request.limit == 25


def test_git_commit_preview_request_rejects_empty_path():
    with pytest.raises(ValidationError):
        GitCommitPreviewRequest(repository_path="")


def test_git_commit_preview_request_rejects_zero_limit():
    with pytest.raises(ValidationError):
        GitCommitPreviewRequest(repository_path="/repo", limit=0)


def test_git_commit_preview_request_rejects_limit_over_100():
    with pytest.raises(ValidationError):
        GitCommitPreviewRequest(repository_path="/repo", limit=101)


def test_git_commit_response_accepts_payload():
    response = make_commit_response("Hello")

    assert response.subject == "Hello"
    assert response.display == "abc Hello"


def test_git_author_contribution_response_accepts_payload():
    response = GitAuthorContributionResponse(
        author_name="A",
        author_email="a@example.com",
        commit_count=2,
    )

    assert response.commit_count == 2


def test_git_commit_preview_summary_response_accepts_payload():
    response = GitCommitPreviewOperatorSummaryResponse(
        outcome="single_author_history",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "single_author_history"


def test_git_commit_preview_response_serializes_nested_payload():
    commit = make_commit_response("Nested")
    response = GitCommitPreviewResponse(
        commit_count=1,
        commits=[commit],
        authors=[
            GitAuthorContributionResponse(
                author_name="A",
                author_email="a@example.com",
                commit_count=1,
            )
        ],
        latest_commit=commit,
        oldest_commit=commit,
        summary=GitCommitPreviewOperatorSummaryResponse(
            outcome="single_author_history",
            message="ok",
            action_required=False,
        ),
    )

    payload = response.model_dump()

    assert payload["commits"][0]["subject"] == "Nested"
    assert payload["latest_commit"]["subject"] == "Nested"
    assert payload["authors"][0]["commit_count"] == 1
