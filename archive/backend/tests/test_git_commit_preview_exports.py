from app.connectors.repository import (
    GitAuthorContribution,
    GitCommitPreview,
    GitCommitPreviewBuilder,
    GitCommitPreviewOperatorSummary,
    GitCommitPreviewSummaryBuilder,
)


def test_git_commit_preview_exports_are_available():
    assert GitAuthorContribution is not None
    assert GitCommitPreview is not None
    assert GitCommitPreviewBuilder is not None


def test_git_commit_preview_summary_exports_are_available():
    assert GitCommitPreviewOperatorSummary is not None
    assert GitCommitPreviewSummaryBuilder is not None
