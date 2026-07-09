from app.connectors.repository import (
    GitIntelligenceProgress,
    GitIntelligenceProgressBuilder,
    RepositoryProgressCheckpoint,
    RepositoryProgressLedger,
    RepositoryProgressLedgerStore,
    RepositoryProgressSummary,
    RepositoryProgressSummaryBuilder,
)


def test_progress_ledger_exports_are_available():
    assert RepositoryProgressCheckpoint is not None
    assert RepositoryProgressLedger is not None
    assert RepositoryProgressLedgerStore is not None


def test_progress_summary_exports_are_available():
    assert RepositoryProgressSummary is not None
    assert RepositoryProgressSummaryBuilder is not None


def test_git_intelligence_progress_exports_are_available():
    assert GitIntelligenceProgress is not None
    assert GitIntelligenceProgressBuilder is not None
