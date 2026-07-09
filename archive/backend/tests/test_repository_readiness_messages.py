from app.connectors.repository import (
    RepositoryObjectiveReadinessEvaluator,
    RepositoryObjectiveSummary,
)


def make_summary(**kwargs):
    defaults = {
        "objective_name": "Repository Ingestion Observability",
        "status": "complete",
        "total_documents": 1,
        "total_processing_jobs": 1,
        "total_failures": 0,
        "total_duplicates": 0,
        "total_unsupported": 0,
        "total_skipped": 0,
        "action_required": False,
    }
    defaults.update(kwargs)
    return RepositoryObjectiveSummary(**defaults)


def test_readiness_success_messages_are_operator_readable():
    report = RepositoryObjectiveReadinessEvaluator().evaluate(make_summary())

    messages = [check.message for check in report.checks]

    assert "Repository ingestion has no recorded failures." in messages
    assert "Repository ingestion created documents." in messages
    assert "Repository ingestion created processing jobs." in messages
    assert "No operator action is required." in messages


def test_readiness_failure_messages_are_operator_readable():
    report = RepositoryObjectiveReadinessEvaluator().evaluate(
        make_summary(
            total_documents=0,
            total_processing_jobs=0,
            total_failures=2,
            action_required=True,
            status="attention_required",
        )
    )

    messages = [check.message for check in report.checks]

    assert "Repository ingestion has 2 recorded failure(s)." in messages
    assert "Repository ingestion has not created any documents." in messages
    assert "Repository ingestion has not created any processing jobs." in messages
    assert "Operator action is required before closing this objective." in messages
