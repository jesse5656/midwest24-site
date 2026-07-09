from app.connectors.repository import (
    RepositoryIngestionFailure,
    RepositoryIngestionReport,
    RepositoryObjectiveCloseoutBuilder,
    RepositoryObjectiveSummaryBuilder,
)


def test_objective_closeout_from_successful_ingestion_reports_is_ready():
    summary = RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
        "Repository Ingestion Observability",
        [
            RepositoryIngestionReport(document_count=2, processing_job_count=2),
            RepositoryIngestionReport(document_count=1, processing_job_count=1),
        ],
    )

    closeout = RepositoryObjectiveCloseoutBuilder().build(summary)

    assert closeout.can_close is True
    assert closeout.status == "ready_to_close"


def test_objective_closeout_from_failed_ingestion_reports_is_not_ready():
    summary = RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
        "Repository Ingestion Observability",
        [
            RepositoryIngestionReport(
                document_count=1,
                processing_job_count=1,
                failures=[RepositoryIngestionFailure(path="bad.md", reason="copy failed")],
            )
        ],
    )

    closeout = RepositoryObjectiveCloseoutBuilder().build(summary)

    assert closeout.can_close is False
    assert closeout.status == "not_ready"
    assert closeout.readiness.failed_count >= 1


def test_objective_closeout_from_empty_ingestion_reports_is_not_ready():
    summary = RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
        "Repository Ingestion Observability",
        [],
    )

    closeout = RepositoryObjectiveCloseoutBuilder().build(summary)

    assert closeout.can_close is False
    assert "documents_created" in [check.name for check in closeout.readiness.failed_checks]


def test_objective_closeout_next_action_changes_by_readiness():
    ready = RepositoryObjectiveCloseoutBuilder().build(
        RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
            "Ready Objective",
            [RepositoryIngestionReport(document_count=1, processing_job_count=1)],
        )
    )
    not_ready = RepositoryObjectiveCloseoutBuilder().build(
        RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
            "Not Ready Objective",
            [],
        )
    )

    assert ready.next_action == "Promote the next Priority Queue item."
    assert "Resolve failed readiness checks" in not_ready.next_action
