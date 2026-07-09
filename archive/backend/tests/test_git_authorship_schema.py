import pytest
from pydantic import ValidationError

from app.schemas.git_authorship_preview import (
    GitAuthorSummaryResponse,
    GitAuthorshipOperatorSummaryResponse,
    GitAuthorshipPreviewRequest,
    GitAuthorshipPreviewResponse,
)


def make_author_response():
    return GitAuthorSummaryResponse(
        author_name="A",
        author_email="a@example.com",
        commit_count=2,
        first_authored_at="2026-01-01T00:00:00Z",
        last_authored_at="2026-01-02T00:00:00Z",
        identity="A <a@example.com>",
    )


def test_authorship_preview_request_defaults_limit():
    request = GitAuthorshipPreviewRequest(repository_path="/repo")

    assert request.limit == 50


def test_authorship_preview_request_accepts_limit():
    request = GitAuthorshipPreviewRequest(repository_path="/repo", limit=100)

    assert request.limit == 100


def test_authorship_preview_request_rejects_empty_path():
    with pytest.raises(ValidationError):
        GitAuthorshipPreviewRequest(repository_path="")


def test_authorship_preview_request_rejects_zero_limit():
    with pytest.raises(ValidationError):
        GitAuthorshipPreviewRequest(repository_path="/repo", limit=0)


def test_authorship_preview_request_rejects_limit_over_250():
    with pytest.raises(ValidationError):
        GitAuthorshipPreviewRequest(repository_path="/repo", limit=251)


def test_author_summary_response_accepts_payload():
    response = make_author_response()

    assert response.identity == "A <a@example.com>"


def test_authorship_summary_response_accepts_payload():
    response = GitAuthorshipOperatorSummaryResponse(
        outcome="single_author",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "single_author"


def test_authorship_preview_response_serializes_nested_payload():
    author = make_author_response()

    response = GitAuthorshipPreviewResponse(
        commit_count=2,
        author_count=1,
        authors=[author],
        top_author=author,
        first_authored_at="2026-01-01T00:00:00Z",
        last_authored_at="2026-01-02T00:00:00Z",
        summary=GitAuthorshipOperatorSummaryResponse(
            outcome="single_author",
            message="ok",
            action_required=False,
        ),
    )

    payload = response.model_dump()

    assert payload["authors"][0]["identity"] == "A <a@example.com>"
    assert payload["top_author"]["commit_count"] == 2
