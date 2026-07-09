import pytest
from pydantic import ValidationError

from app.schemas.code_intelligence_report import (
    CodeIntelligenceCloseoutResponse,
    CodeIntelligenceOperatorSummaryResponse,
    CodeIntelligenceReadinessCheckResponse,
    CodeIntelligenceReadinessReportResponse,
    CodeIntelligenceReportRequest,
)


def test_code_intelligence_report_request_accepts_path():
    request = CodeIntelligenceReportRequest(repository_path="/repo")

    assert request.repository_path == "/repo"


def test_code_intelligence_report_request_rejects_empty_path():
    with pytest.raises(ValidationError):
        CodeIntelligenceReportRequest(repository_path="")


def test_code_intelligence_summary_response_accepts_payload():
    response = CodeIntelligenceOperatorSummaryResponse(
        outcome="ready",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "ready"


def test_code_intelligence_readiness_check_response_accepts_payload():
    response = CodeIntelligenceReadinessCheckResponse(
        name="has_inventory",
        passed=True,
        message="ok",
    )

    assert response.name == "has_inventory"


def test_code_intelligence_readiness_report_response_accepts_payload():
    response = CodeIntelligenceReadinessReportResponse(
        checks=[
            CodeIntelligenceReadinessCheckResponse(
                name="has_inventory",
                passed=True,
                message="ok",
            )
        ],
        passed=True,
        passed_count=1,
        failed_count=0,
    )

    assert response.passed_count == 1


def test_code_intelligence_closeout_response_accepts_payload():
    response = CodeIntelligenceCloseoutResponse(
        objective_name="Code Intelligence Preview",
        status="ready_to_close",
        can_close=True,
        readiness=CodeIntelligenceReadinessReportResponse(
            checks=[],
            passed=True,
            passed_count=0,
            failed_count=0,
        ),
        next_action="Promote the next Priority Queue item.",
    )

    assert response.can_close is True
