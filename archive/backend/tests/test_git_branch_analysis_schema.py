import pytest
from pydantic import ValidationError

from app.schemas.git_branch_analysis import (
    GitBranchAnalysisOperatorSummaryResponse,
    GitBranchAnalysisRequest,
    GitBranchAnalysisResponse,
    GitBranchResponse,
)


def test_branch_analysis_request_accepts_path():
    request = GitBranchAnalysisRequest(repository_path="/repo")

    assert request.repository_path == "/repo"


def test_branch_analysis_request_rejects_empty_path():
    with pytest.raises(ValidationError):
        GitBranchAnalysisRequest(repository_path="")


def test_branch_response_accepts_payload():
    response = GitBranchResponse(name="main", current=True)

    assert response.name == "main"
    assert response.current is True


def test_branch_analysis_summary_response_accepts_payload():
    response = GitBranchAnalysisOperatorSummaryResponse(
        outcome="single_branch",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "single_branch"


def test_branch_analysis_response_serializes_nested_payload():
    branch = GitBranchResponse(name="main", current=True)

    response = GitBranchAnalysisResponse(
        branch_count=1,
        branches=[branch],
        current_branch=branch,
        current_branch_name="main",
        has_multiple_branches=False,
        branch_names=["main"],
        non_current_branch_names=[],
        summary=GitBranchAnalysisOperatorSummaryResponse(
            outcome="single_branch",
            message="ok",
            action_required=False,
        ),
    )

    payload = response.model_dump()

    assert payload["branches"][0]["name"] == "main"
    assert payload["current_branch"]["current"] is True
    assert payload["summary"]["outcome"] == "single_branch"


def test_branch_analysis_response_accepts_null_current_branch():
    response = GitBranchAnalysisResponse(
        branch_count=0,
        branches=[],
        current_branch=None,
        current_branch_name=None,
        has_multiple_branches=False,
        branch_names=[],
        non_current_branch_names=[],
        summary=GitBranchAnalysisOperatorSummaryResponse(
            outcome="no_branches",
            message="ok",
            action_required=False,
        ),
    )

    assert response.current_branch is None
    assert response.current_branch_name is None
