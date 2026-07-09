from app.connectors.repository import GitCommit, GitCommitPreview, GitCommitPreviewSummaryBuilder


def make_commit(author_name="A", author_email="a@example.com"):
    return GitCommit(
        sha="a",
        short_sha="a",
        author_name=author_name,
        author_email=author_email,
        authored_at="2026-01-01T00:00:00Z",
        subject="Subject",
    )


def test_git_commit_preview_summary_reports_no_commits():
    summary = GitCommitPreviewSummaryBuilder().build(GitCommitPreview())

    assert summary.outcome == "no_commits"
    assert summary.action_required is False
    assert "No commits" in summary.message


def test_git_commit_preview_summary_reports_single_author_history():
    preview = GitCommitPreview(commits=[make_commit(), make_commit()])

    summary = GitCommitPreviewSummaryBuilder().build(preview)

    assert summary.outcome == "single_author_history"
    assert summary.action_required is False
    assert "2 commit" in summary.message


def test_git_commit_preview_summary_reports_multi_author_history():
    preview = GitCommitPreview(
        commits=[
            make_commit(author_name="A", author_email="a@example.com"),
            make_commit(author_name="B", author_email="b@example.com"),
        ]
    )

    summary = GitCommitPreviewSummaryBuilder().build(preview)

    assert summary.outcome == "multi_author_history"
    assert summary.action_required is False
    assert "2 author" in summary.message


def test_git_commit_preview_summary_counts_multiple_authors_once_each():
    preview = GitCommitPreview(
        commits=[
            make_commit(author_name="A", author_email="a@example.com"),
            make_commit(author_name="A", author_email="a@example.com"),
            make_commit(author_name="B", author_email="b@example.com"),
        ]
    )

    summary = GitCommitPreviewSummaryBuilder().build(preview)

    assert summary.outcome == "multi_author_history"
    assert "2 author" in summary.message
