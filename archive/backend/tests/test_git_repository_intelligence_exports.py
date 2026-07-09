from app.connectors.repository import (
    GitRepositoryOperatorSummary,
    GitRepositoryOperatorSummaryBuilder,
)


def test_git_operator_summary_exports_are_available():
    assert GitRepositoryOperatorSummary is not None
    assert GitRepositoryOperatorSummaryBuilder is not None


def test_git_operator_summary_dataclass_preserves_fields():
    summary = GitRepositoryOperatorSummary(
        outcome="repository_clean",
        message="ok",
        action_required=False,
    )

    assert summary.outcome == "repository_clean"
    assert summary.message == "ok"
    assert summary.action_required is False
