from app.connectors.repository import (
    RepositoryProgressCheckpoint,
    RepositoryProgressLedger,
    RepositoryProgressSummaryBuilder,
)


def test_progress_summary_reports_empty_ledger():
    summary = RepositoryProgressSummaryBuilder().build(
        RepositoryProgressLedger(repository="midwest24-site")
    )

    assert summary.status == "empty"
    assert summary.latest_test_count == 0
    assert "No progress checkpoints" in summary.message


def test_progress_summary_reports_latest_checkpoint():
    ledger = RepositoryProgressLedger(
        repository="midwest24-site",
        checkpoints=[
            RepositoryProgressCheckpoint(name="A", test_count=100, status="completed"),
            RepositoryProgressCheckpoint(name="B", test_count=200, status="in_progress"),
        ],
    )

    summary = RepositoryProgressSummaryBuilder().build(ledger)

    assert summary.repository == "midwest24-site"
    assert summary.latest_test_count == 200
    assert summary.checkpoint_count == 2
    assert summary.completed_count == 1
    assert summary.status == "in_progress"
    assert "B" in summary.message


def test_progress_summary_message_mentions_test_count():
    ledger = RepositoryProgressLedger(
        repository="midwest24-site",
        checkpoints=[
            RepositoryProgressCheckpoint(name="A", test_count=443, status="completed"),
        ],
    )

    summary = RepositoryProgressSummaryBuilder().build(ledger)

    assert "443 passing tests" in summary.message
