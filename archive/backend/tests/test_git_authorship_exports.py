from app.connectors.repository import (
    GitAuthorSummary,
    GitAuthorshipOperatorSummary,
    GitAuthorshipPreview,
    GitAuthorshipPreviewBuilder,
    GitAuthorshipSummaryBuilder,
)


def test_git_authorship_exports_are_available():
    assert GitAuthorSummary is not None
    assert GitAuthorshipPreview is not None
    assert GitAuthorshipPreviewBuilder is not None


def test_git_authorship_summary_exports_are_available():
    assert GitAuthorshipOperatorSummary is not None
    assert GitAuthorshipSummaryBuilder is not None
