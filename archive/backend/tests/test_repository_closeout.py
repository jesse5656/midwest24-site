from app.connectors.repository import (
    RepositoryObjectiveCloseoutBuilder,
    RepositoryObjectiveSummary,
)


def make_summary(
    total_documents=1,
    total_processing_jobs=1,
    total_failures=0,
    action_required=False,
    status="complete",
):
    return RepositoryObjectiveSummary(
        objective_name="Repository Ingestion Observability",
        status=status,
        total_documents=total_documents,
        total_processing_jobs=total_processing_jobs,
        total_failures=total_failures,
        total_duplicates=0,
        total_unsupported=0,
        total_skipped=0,
        action_required=action_required,
    )


def test_closeout_builder_marks_ready_to_close_when_summary_and_readiness_pass():
    closeout = RepositoryObjectiveCloseoutBuilder().build(make_summary())

    assert closeout.objective_name == "Repository Ingestion Observability"
    assert closeout.status == "ready_to_close"
    assert closeout.can_close is True
    assert closeout.readiness.passed is True
    assert closeout.next_action == "Promote the next Priority Queue item."


def test_closeout_builder_marks_not_ready_when_failures_exist():
    closeout = RepositoryObjectiveCloseoutBuilder().build(
        make_summary(total_failures=1, action_required=True, status="attention_required")
    )

    assert closeout.status == "not_ready"
    assert closeout.can_close is False
    assert closeout.readiness.passed is False


def test_closeout_builder_marks_not_ready_when_no_documents_exist():
    closeout = RepositoryObjectiveCloseoutBuilder().build(
        make_summary(total_documents=0)
    )

    assert closeout.status == "not_ready"
    assert closeout.can_close is False
    assert "Resolve failed readiness checks" in closeout.next_action


def test_closeout_builder_marks_not_ready_when_no_jobs_exist():
    closeout = RepositoryObjectiveCloseoutBuilder().build(
        make_summary(total_processing_jobs=0)
    )

    assert closeout.status == "not_ready"
    assert closeout.can_close is False


def test_closeout_builder_uses_summary_is_complete_gate():
    summary = make_summary(status="attention_required", action_required=False)
    closeout = RepositoryObjectiveCloseoutBuilder().build(summary)

    assert summary.is_complete is False
    assert closeout.can_close is False


def test_closeout_builder_exposes_failed_readiness_checks():
    closeout = RepositoryObjectiveCloseoutBuilder().build(
        make_summary(total_documents=0, total_processing_jobs=0)
    )

    failed_names = [check.name for check in closeout.readiness.failed_checks]

    assert "documents_created" in failed_names
    assert "jobs_created" in failed_names
