import pytest
from pydantic import ValidationError

from app.schemas.git_objective_scorecard import (
    GitObjectiveCapabilityResponse,
    GitObjectiveOperatorSummaryResponse,
    GitObjectiveScorecardRequest,
    GitObjectiveScorecardResponse,
)


def test_scorecard_request_accepts_test_count():
    request = GitObjectiveScorecardRequest(test_count=473)

    assert request.test_count == 473


def test_scorecard_request_rejects_negative_test_count():
    with pytest.raises(ValidationError):
        GitObjectiveScorecardRequest(test_count=-1)


def test_capability_response_accepts_payload():
    response = GitObjectiveCapabilityResponse(
        name="api",
        completed=True,
        evidence="exists",
    )

    assert response.completed is True


def test_objective_summary_response_accepts_payload():
    response = GitObjectiveOperatorSummaryResponse(
        outcome="complete",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "complete"


def test_scorecard_response_serializes_nested_payload():
    response = GitObjectiveScorecardResponse(
        objective_name="Git Repository Intelligence",
        capabilities=[
            GitObjectiveCapabilityResponse(
                name="api",
                completed=True,
                evidence="exists",
            )
        ],
        test_count=473,
        capability_count=1,
        completed_capability_count=1,
        incomplete_capability_count=0,
        completion_ratio=1.0,
        is_complete=True,
        summary=GitObjectiveOperatorSummaryResponse(
            outcome="complete",
            message="ok",
            action_required=False,
        ),
    )

    payload = response.model_dump()

    assert payload["capabilities"][0]["name"] == "api"
    assert payload["summary"]["outcome"] == "complete"
