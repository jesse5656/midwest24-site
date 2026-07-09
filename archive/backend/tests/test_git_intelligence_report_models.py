from app.connectors.repository import (
    GitAuthorshipPreview,
    GitCommit,
    GitCommitPreview,
    GitCommitFileChangeSet,
    GitFileChange,
    GitFileChangePreview,
    GitIntelligenceReport,
    GitRepositorySummary,
)


def make_commit(author_name="A", author_email="a@example.com"):
    return GitCommit(
        sha="abcdef",
        short_sha="abc",
        author_name=author_name,
        author_email=author_email,
        authored_at="2026-01-01T00:00:00Z",
        subject="Subject",
    )


def make_report(is_repository=True, is_clean=True, commits=None, file_changes=None, authorship=None):
    commits = commits if commits is not None else GitCommitPreview(commits=[make_commit()])
    authorship = authorship if authorship is not None else GitAuthorshipPreview(commits=[make_commit()])
    file_changes = file_changes if file_changes is not None else GitFileChangePreview(
        commits=[
            GitCommitFileChangeSet(
                commit_sha="abcdef",
                short_sha="abc",
                subject="Subject",
                files=[GitFileChange(status="M", path="README.md")],
            )
        ]
    )

    return GitIntelligenceReport(
        repository=GitRepositorySummary(
            is_repository=is_repository,
            root="/repo" if is_repository else None,
            current_branch="main" if is_repository else None,
            recent_commit_count=commits.commit_count,
            is_clean=is_clean if is_repository else None,
        ),
        commits=commits,
        file_changes=file_changes,
        authorship=authorship,
    )


def test_git_intelligence_report_exposes_repository_flag():
    assert make_report().is_repository is True


def test_git_intelligence_report_exposes_current_branch():
    assert make_report().current_branch == "main"


def test_git_intelligence_report_counts_commits():
    assert make_report().commit_count == 1


def test_git_intelligence_report_counts_file_changes():
    assert make_report().file_change_count == 1


def test_git_intelligence_report_counts_authors():
    assert make_report().author_count == 1


def test_git_intelligence_report_detects_uncommitted_changes():
    assert make_report(is_clean=False).has_uncommitted_changes is True


def test_git_intelligence_report_ready_when_repo_has_commits_and_authors():
    assert make_report().is_ready is True


def test_git_intelligence_report_not_ready_when_not_repository():
    assert make_report(is_repository=False).is_ready is False


def test_git_intelligence_report_not_ready_without_commits():
    report = make_report(commits=GitCommitPreview(), authorship=GitAuthorshipPreview())

    assert report.is_ready is False
