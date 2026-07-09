import pytest
from pydantic import ValidationError

from app.schemas.backend_milestone import (
    BackendMilestoneCapabilityResponse,
    BackendMilestoneCloseoutResponse,
    BackendMilestoneOperatorSummaryResponse,
    BackendMilestoneReadinessCheckResponse,
    BackendMilestoneReadinessReportResponse,
    BackendMilestoneScorecardRequest,
    BackendMilestoneScorecardResponse,
)


def test_backend_milestone_request_accepts_test_count():
    request = BackendMilestoneScorecardRequest(test_count=721)

    assert request.test_count == 721


def test_backend_milestone_request_rejects_negative_test_count():
    with pytest.raises(ValidationError):
        BackendMilestoneScorecardRequest(test_count=-1)


def test_backend_milestone_capability_response_accepts_payload():
    response = BackendMilestoneCapabilityResponse(
        name="api",
        completed=True,
        evidence="exists",
    )

    assert response.completed is True


def test_backend_milestone_summary_response_accepts_payload():
    response = BackendMilestoneOperatorSummaryResponse(
        outcome="complete",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "complete"


def test_backend_milestone_readiness_response_accepts_payload():
    response = BackendMilestoneReadinessReportResponse(
        checks=[
            BackendMilestoneReadinessCheckResponse(
                name="has_tests",
                passed=True,
                message="ok",
            )
        ],
        passed=True,
        passed_count=1,
        failed_count=0,
    )

    assert response.passed is True


def test_backend_milestone_closeout_response_accepts_payload():
    response = BackendMilestoneCloseoutResponse(
        milestone_name="Archive Backend Milestone",
        status="ready_to_close",
        can_close=True,
        readiness=BackendMilestoneReadinessReportResponse(
            checks=[],
            passed=True,
            passed_count=0,
            failed_count=0,
        ),
        next_action="Prepare session transition prompt.",
    )

    assert response.can_close is True


def test_backend_milestone_scorecard_response_serializes_nested_payload():
    response = BackendMilestoneScorecardResponse(
        milestone_name="Archive Backend Milestone",
        test_count=721,
        capabilities=[
            BackendMilestoneCapabilityResponse(
                name="api",
                completed=True,
                evidence="exists",
            )
        ],
        capability_count=1,
        completed_capability_count=1,
        incomplete_capability_count=0,
        completion_ratio=1.0,
        is_complete=True,
        summary=BackendMilestoneOperatorSummaryResponse(
            outcome="complete",
            message="ok",
            action_required=False,
        ),
        closeout=BackendMilestoneCloseoutResponse(
            milestone_name="Archive Backend Milestone",
            status="ready_to_close",
            can_close=True,
            readiness=BackendMilestoneReadinessReportResponse(
                checks=[],
                passed=True,
                passed_count=0,
                failed_count=0,
            ),
            next_action="Prepare session transition prompt.",
        ),
    )

    payload = response.model_dump()

    assert payload["capabilities"][0]["name"] == "api"
    assert payload["closeout"]["can_close"] is True
