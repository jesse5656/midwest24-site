import pytest
from pydantic import ValidationError

from app.schemas.git_intelligence_report import (
    GitIntelligenceCloseoutResponse,
    GitIntelligenceOperatorSummaryResponse,
    GitIntelligenceReadinessCheckResponse,
    GitIntelligenceReadinessReportResponse,
    GitIntelligenceReportRequest,
)


def test_git_intelligence_report_request_defaults_limit():
    request = GitIntelligenceReportRequest(repository_path="/repo")

    assert request.limit == 25


def test_git_intelligence_report_request_rejects_empty_path():
    with pytest.raises(ValidationError):
        GitIntelligenceReportRequest(repository_path="")


def test_git_intelligence_report_request_rejects_zero_limit():
    with pytest.raises(ValidationError):
        GitIntelligenceReportRequest(repository_path="/repo", limit=0)


def test_git_intelligence_report_request_rejects_limit_over_100():
    with pytest.raises(ValidationError):
        GitIntelligenceReportRequest(repository_path="/repo", limit=101)


def test_git_intelligence_summary_response_accepts_payload():
    response = GitIntelligenceOperatorSummaryResponse(
        outcome="ready",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "ready"


def test_git_intelligence_readiness_check_response_accepts_payload():
    response = GitIntelligenceReadinessCheckResponse(
        name="has_commits",
        passed=True,
        message="ok",
    )

    assert response.name == "has_commits"


def test_git_intelligence_readiness_report_response_accepts_payload():
    response = GitIntelligenceReadinessReportResponse(
        checks=[
            GitIntelligenceReadinessCheckResponse(
                name="has_commits",
                passed=True,
                message="ok",
            )
        ],
        passed=True,
        passed_count=1,
        failed_count=0,
    )

    assert response.passed_count == 1


def test_git_intelligence_closeout_response_accepts_payload():
    response = GitIntelligenceCloseoutResponse(
        objective_name="Git Repository Intelligence",
        status="ready_to_close",
        can_close=True,
        readiness=GitIntelligenceReadinessReportResponse(
            checks=[],
            passed=True,
            passed_count=0,
            failed_count=0,
        ),
        next_action="Promote the next Priority Queue item.",
    )

    assert response.can_close is True
