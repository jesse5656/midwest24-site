from app.connectors.repository import GitAuthorshipPreview, GitAuthorshipSummaryBuilder, GitCommit


def make_commit(author_name="A", author_email="a@example.com"):
    return GitCommit(
        sha="abcdef",
        short_sha="abc",
        author_name=author_name,
        author_email=author_email,
        authored_at="2026-01-01T00:00:00Z",
        subject="Subject",
    )


def test_authorship_summary_reports_no_authorship():
    summary = GitAuthorshipSummaryBuilder().build(GitAuthorshipPreview())

    assert summary.outcome == "no_authorship"
    assert summary.action_required is False
    assert "No Git authorship" in summary.message


def test_authorship_summary_reports_single_author():
    preview = GitAuthorshipPreview(commits=[make_commit(), make_commit()])

    summary = GitAuthorshipSummaryBuilder().build(preview)

    assert summary.outcome == "single_author"
    assert summary.action_required is False
    assert "2 commit" in summary.message


def test_authorship_summary_single_author_mentions_identity():
    preview = GitAuthorshipPreview(commits=[make_commit("A", "a@example.com")])

    summary = GitAuthorshipSummaryBuilder().build(preview)

    assert "A <a@example.com>" in summary.message


def test_authorship_summary_reports_multiple_authors():
    preview = GitAuthorshipPreview(
        commits=[
            make_commit("A", "a@example.com"),
            make_commit("B", "b@example.com"),
        ]
    )

    summary = GitAuthorshipSummaryBuilder().build(preview)

    assert summary.outcome == "multiple_authors"
    assert summary.action_required is False
    assert "2 author" in summary.message
