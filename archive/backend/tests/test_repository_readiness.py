from app.connectors.repository import (
    RepositoryIngestionFailure,
    RepositoryObjectiveReadinessEvaluator,
    RepositoryObjectiveSummary,
    RepositoryReadinessCheck,
    RepositoryReadinessReport,
)


def test_readiness_report_passes_when_all_checks_pass():
    report = RepositoryReadinessReport(
        checks=[
            RepositoryReadinessCheck(name="a", passed=True, message="ok"),
            RepositoryReadinessCheck(name="b", passed=True, message="ok"),
        ]
    )

    assert report.passed is True
    assert report.failed_checks == []
    assert report.passed_count == 2
    assert report.failed_count == 0


def test_readiness_report_fails_when_any_check_fails():
    report = RepositoryReadinessReport(
        checks=[
            RepositoryReadinessCheck(name="a", passed=True, message="ok"),
            RepositoryReadinessCheck(name="b", passed=False, message="bad"),
        ]
    )

    assert report.passed is False
    assert len(report.failed_checks) == 1
    assert report.failed_checks[0].name == "b"
    assert report.passed_count == 1
    assert report.failed_count == 1


def test_readiness_evaluator_passes_complete_repository_summary():
    summary = RepositoryObjectiveSummary(
        objective_name="Repository Ingestion Observability",
        status="complete",
        total_documents=1,
        total_processing_jobs=1,
        total_failures=0,
        total_duplicates=0,
        total_unsupported=0,
        total_skipped=0,
        action_required=False,
    )

    report = RepositoryObjectiveReadinessEvaluator().evaluate(summary)

    assert report.passed is True
    assert report.failed_count == 0


def test_readiness_evaluator_fails_when_failures_exist():
    summary = RepositoryObjectiveSummary(
        objective_name="Repository Ingestion Observability",
        status="attention_required",
        total_documents=1,
        total_processing_jobs=1,
        total_failures=1,
        total_duplicates=0,
        total_unsupported=0,
        total_skipped=0,
        action_required=True,
    )

    report = RepositoryObjectiveReadinessEvaluator().evaluate(summary)

    assert report.passed is False
    assert "no_failures" in [check.name for check in report.failed_checks]


def test_readiness_evaluator_fails_when_no_documents_created():
    summary = RepositoryObjectiveSummary(
        objective_name="Repository Ingestion Observability",
        status="complete",
        total_documents=0,
        total_processing_jobs=1,
        total_failures=0,
        total_duplicates=0,
        total_unsupported=0,
        total_skipped=0,
        action_required=False,
    )

    report = RepositoryObjectiveReadinessEvaluator().evaluate(summary)

    assert report.passed is False
    assert "documents_created" in [check.name for check in report.failed_checks]


def test_readiness_evaluator_fails_when_no_jobs_created():
    summary = RepositoryObjectiveSummary(
        objective_name="Repository Ingestion Observability",
        status="complete",
        total_documents=1,
        total_processing_jobs=0,
        total_failures=0,
        total_duplicates=0,
        total_unsupported=0,
        total_skipped=0,
        action_required=False,
    )

    report = RepositoryObjectiveReadinessEvaluator().evaluate(summary)

    assert report.passed is False
    assert "jobs_created" in [check.name for check in report.failed_checks]


def test_readiness_evaluator_fails_when_action_required():
    summary = RepositoryObjectiveSummary(
        objective_name="Repository Ingestion Observability",
        status="attention_required",
        total_documents=1,
        total_processing_jobs=1,
        total_failures=0,
        total_duplicates=0,
        total_unsupported=0,
        total_skipped=0,
        action_required=True,
    )

    report = RepositoryObjectiveReadinessEvaluator().evaluate(summary)

    assert report.passed is False
    assert "no_action_required" in [check.name for check in report.failed_checks]


def test_readiness_check_preserves_message():
    check = RepositoryReadinessCheck(
        name="docs",
        passed=False,
        message="Repository ingestion has not created any documents.",
    )

    assert check.message == "Repository ingestion has not created any documents."
