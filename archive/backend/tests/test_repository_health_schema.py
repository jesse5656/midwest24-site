import pytest
from pydantic import ValidationError

from app.schemas.repository_health import (
    ArchiveBackendHealthRequest,
    RepositoryHealthCheckResponse,
    RepositoryHealthOperatorSummaryResponse,
    RepositoryHealthReportResponse,
)


def test_archive_backend_health_request_defaults_flags():
    request = ArchiveBackendHealthRequest(test_count=684)

    assert request.has_progress_ledger is True
    assert request.has_operating_plan is True


def test_archive_backend_health_request_rejects_negative_test_count():
    with pytest.raises(ValidationError):
        ArchiveBackendHealthRequest(test_count=-1)


def test_health_check_response_accepts_payload():
    response = RepositoryHealthCheckResponse(
        name="tests_present",
        passed=True,
        message="ok",
        severity="info",
    )

    assert response.name == "tests_present"


def test_health_summary_response_accepts_payload():
    response = RepositoryHealthOperatorSummaryResponse(
        outcome="healthy",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "healthy"


def test_health_report_response_serializes_nested_payload():
    response = RepositoryHealthReportResponse(
        name="Health",
        checks=[
            RepositoryHealthCheckResponse(
                name="tests_present",
                passed=True,
                message="ok",
                severity="info",
            )
        ],
        passed=True,
        check_count=1,
        passed_count=1,
        failed_count=0,
        warning_count=0,
        error_count=0,
        summary=RepositoryHealthOperatorSummaryResponse(
            outcome="healthy",
            message="ok",
            action_required=False,
        ),
    )

    payload = response.model_dump()

    assert payload["checks"][0]["name"] == "tests_present"
    assert payload["summary"]["outcome"] == "healthy"
