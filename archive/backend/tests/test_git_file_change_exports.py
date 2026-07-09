from app.connectors.repository import (
    GitCommitFileChangeSet,
    GitFileChange,
    GitFileChangeParser,
    GitFileChangePreview,
    GitFileChangePreviewBuilder,
    GitFileChangeOperatorSummary,
    GitFileChangeSummaryBuilder,
)


def test_git_file_change_exports_are_available():
    assert GitFileChange is not None
    assert GitCommitFileChangeSet is not None
    assert GitFileChangePreview is not None
    assert GitFileChangeParser is not None
    assert GitFileChangePreviewBuilder is not None


def test_git_file_change_summary_exports_are_available():
    assert GitFileChangeOperatorSummary is not None
    assert GitFileChangeSummaryBuilder is not None
