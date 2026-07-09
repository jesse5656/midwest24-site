from app.connectors.repository import (
    GitCommitFileChangeSet,
    GitFileChange,
    GitFileChangePreview,
    GitFileChangeSummaryBuilder,
)


def test_file_change_summary_reports_no_file_changes():
    summary = GitFileChangeSummaryBuilder().build(GitFileChangePreview())

    assert summary.outcome == "no_file_changes"
    assert summary.action_required is False
    assert "No Git file changes" in summary.message


def test_file_change_summary_reports_commits_without_file_changes():
    preview = GitFileChangePreview(
        commits=[
            GitCommitFileChangeSet(commit_sha="a", short_sha="a", subject="A", files=[])
        ]
    )

    summary = GitFileChangeSummaryBuilder().build(preview)

    assert summary.outcome == "commits_without_file_changes"
    assert "without file-change entries" in summary.message


def test_file_change_summary_reports_file_changes_found():
    preview = GitFileChangePreview(
        commits=[
            GitCommitFileChangeSet(
                commit_sha="a",
                short_sha="a",
                subject="A",
                files=[GitFileChange(status="M", path="README.md")],
            )
        ]
    )

    summary = GitFileChangeSummaryBuilder().build(preview)

    assert summary.outcome == "file_changes_found"
    assert summary.action_required is False
    assert "1 file change" in summary.message


def test_file_change_summary_mentions_commit_count():
    preview = GitFileChangePreview(
        commits=[
            GitCommitFileChangeSet(
                commit_sha="a",
                short_sha="a",
                subject="A",
                files=[GitFileChange(status="M", path="README.md")],
            ),
            GitCommitFileChangeSet(
                commit_sha="b",
                short_sha="b",
                subject="B",
                files=[GitFileChange(status="A", path="PLAN.md")],
            ),
        ]
    )

    summary = GitFileChangeSummaryBuilder().build(preview)

    assert "2 commit" in summary.message
