from pydantic import ValidationError
import pytest

from app.schemas.git_repository_intelligence import (
    GitRepositoryIntelligenceEnvelopeResponse,
    GitRepositoryIntelligenceRequest,
    GitRepositoryIntelligenceResponse,
    GitRepositoryOperatorSummaryResponse,
)


def test_git_intelligence_request_defaults_commit_limit():
    request = GitRepositoryIntelligenceRequest(repository_path="/repo")

    assert request.repository_path == "/repo"
    assert request.commit_limit == 5


def test_git_intelligence_request_accepts_custom_commit_limit():
    request = GitRepositoryIntelligenceRequest(repository_path="/repo", commit_limit=25)

    assert request.commit_limit == 25


def test_git_intelligence_request_rejects_empty_path():
    with pytest.raises(ValidationError):
        GitRepositoryIntelligenceRequest(repository_path="")


def test_git_intelligence_request_rejects_zero_commit_limit():
    with pytest.raises(ValidationError):
        GitRepositoryIntelligenceRequest(repository_path="/repo", commit_limit=0)


def test_git_intelligence_request_rejects_commit_limit_over_50():
    with pytest.raises(ValidationError):
        GitRepositoryIntelligenceRequest(repository_path="/repo", commit_limit=51)


def test_git_intelligence_response_accepts_repository_payload():
    response = GitRepositoryIntelligenceResponse(
        is_repository=True,
        root="/repo",
        current_branch="main",
        recent_commit_count=5,
        is_clean=True,
    )

    assert response.is_repository is True
    assert response.current_branch == "main"


def test_git_intelligence_response_accepts_non_repository_payload():
    response = GitRepositoryIntelligenceResponse(
        is_repository=False,
        root=None,
        current_branch=None,
        recent_commit_count=0,
        is_clean=None,
    )

    assert response.root is None
    assert response.is_clean is None


def test_git_operator_summary_response_accepts_payload():
    response = GitRepositoryOperatorSummaryResponse(
        outcome="repository_clean",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "repository_clean"


def test_git_intelligence_envelope_response_serializes_nested_payload():
    response = GitRepositoryIntelligenceEnvelopeResponse(
        intelligence=GitRepositoryIntelligenceResponse(
            is_repository=True,
            root="/repo",
            current_branch="main",
            recent_commit_count=5,
            is_clean=True,
        ),
        summary=GitRepositoryOperatorSummaryResponse(
            outcome="repository_clean",
            message="ok",
            action_required=False,
        ),
    )

    payload = response.model_dump()

    assert payload["intelligence"]["root"] == "/repo"
    assert payload["summary"]["outcome"] == "repository_clean"
