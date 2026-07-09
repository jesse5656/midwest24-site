from app.schemas.repository_readiness import (
    RepositoryObjectiveCloseoutResponse,
    RepositoryReadinessCheckResponse,
    RepositoryReadinessReportResponse,
)


def test_readiness_check_response_accepts_payload():
    response = RepositoryReadinessCheckResponse(
        name="no_failures",
        passed=True,
        message="Repository ingestion has no recorded failures.",
    )

    assert response.name == "no_failures"
    assert response.passed is True


def test_readiness_report_response_accepts_payload():
    response = RepositoryReadinessReportResponse(
        checks=[
            RepositoryReadinessCheckResponse(
                name="no_failures",
                passed=True,
                message="ok",
            )
        ],
        passed=True,
        passed_count=1,
        failed_count=0,
    )

    assert response.passed is True
    assert response.passed_count == 1
    assert response.failed_count == 0


def test_readiness_report_response_serializes_nested_checks():
    response = RepositoryReadinessReportResponse(
        checks=[
            RepositoryReadinessCheckResponse(
                name="documents_created",
                passed=False,
                message="missing",
            )
        ],
        passed=False,
        passed_count=0,
        failed_count=1,
    )

    payload = response.model_dump()

    assert payload["checks"][0]["name"] == "documents_created"
    assert payload["failed_count"] == 1


def test_objective_closeout_response_accepts_ready_payload():
    response = RepositoryObjectiveCloseoutResponse(
        objective_name="Repository Ingestion Observability",
        status="ready_to_close",
        can_close=True,
        readiness=RepositoryReadinessReportResponse(
            checks=[],
            passed=True,
            passed_count=0,
            failed_count=0,
        ),
        next_action="Promote the next Priority Queue item.",
    )

    assert response.can_close is True
    assert response.status == "ready_to_close"


def test_objective_closeout_response_accepts_not_ready_payload():
    response = RepositoryObjectiveCloseoutResponse(
        objective_name="Repository Ingestion Observability",
        status="not_ready",
        can_close=False,
        readiness=RepositoryReadinessReportResponse(
            checks=[
                RepositoryReadinessCheckResponse(
                    name="no_failures",
                    passed=False,
                    message="bad",
                )
            ],
            passed=False,
            passed_count=0,
            failed_count=1,
        ),
        next_action="Resolve failed readiness checks before closing the objective.",
    )

    assert response.can_close is False
    assert response.readiness.failed_count == 1
