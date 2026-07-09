import pytest
from pydantic import ValidationError

from app.schemas.code_objective_scorecard import (
    CodeObjectiveCapabilityResponse,
    CodeObjectiveOperatorSummaryResponse,
    CodeObjectiveScorecardRequest,
    CodeObjectiveScorecardResponse,
)


def test_code_scorecard_request_accepts_test_count():
    request = CodeObjectiveScorecardRequest(test_count=645)

    assert request.test_count == 645


def test_code_scorecard_request_rejects_negative_test_count():
    with pytest.raises(ValidationError):
        CodeObjectiveScorecardRequest(test_count=-1)


def test_code_capability_response_accepts_payload():
    response = CodeObjectiveCapabilityResponse(
        name="api",
        completed=True,
        evidence="exists",
    )

    assert response.completed is True


def test_code_objective_summary_response_accepts_payload():
    response = CodeObjectiveOperatorSummaryResponse(
        outcome="complete",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "complete"


def test_code_scorecard_response_serializes_nested_payload():
    response = CodeObjectiveScorecardResponse(
        objective_name="Code Intelligence Preview",
        capabilities=[
            CodeObjectiveCapabilityResponse(
                name="api",
                completed=True,
                evidence="exists",
            )
        ],
        test_count=645,
        capability_count=1,
        completed_capability_count=1,
        incomplete_capability_count=0,
        completion_ratio=1.0,
        is_complete=True,
        summary=CodeObjectiveOperatorSummaryResponse(
            outcome="complete",
            message="ok",
            action_required=False,
        ),
    )

    payload = response.model_dump()

    assert payload["capabilities"][0]["name"] == "api"
    assert payload["summary"]["outcome"] == "complete"
