from app.connectors.repository import (
    GitAuthorshipPreview,
    GitCommit,
    GitCommitPreview,
    GitCommitFileChangeSet,
    GitFileChange,
    GitFileChangePreview,
    GitIntelligenceProgressBuilder,
    GitIntelligenceReport,
    GitRepositorySummary,
)


def make_commit():
    return GitCommit(
        sha="abcdef",
        short_sha="abc",
        author_name="A",
        author_email="a@example.com",
        authored_at="2026-01-01T00:00:00Z",
        subject="Subject",
    )


def make_report(is_repository=True, current_branch="main", is_clean=True, commits=True, authors=True):
    commit = make_commit()
    return GitIntelligenceReport(
        repository=GitRepositorySummary(
            is_repository=is_repository,
            root="/repo" if is_repository else None,
            current_branch=current_branch,
            recent_commit_count=1 if commits else 0,
            is_clean=is_clean if is_repository else None,
        ),
        commits=GitCommitPreview(commits=[commit] if commits else []),
        file_changes=GitFileChangePreview(
            commits=[
                GitCommitFileChangeSet(
                    commit_sha="abcdef",
                    short_sha="abc",
                    subject="Subject",
                    files=[GitFileChange(status="M", path="README.md")],
                )
            ]
        ),
        authorship=GitAuthorshipPreview(commits=[commit] if authors else []),
    )


def test_git_intelligence_progress_reports_completed_when_ready():
    progress = GitIntelligenceProgressBuilder().build(make_report(), test_count=443)

    assert progress.objective_name == "Git Repository Intelligence"
    assert progress.status == "completed"
    assert progress.test_count == 443


def test_git_intelligence_progress_reports_in_progress_when_not_ready():
    progress = GitIntelligenceProgressBuilder().build(
        make_report(is_repository=False, current_branch=None, commits=False, authors=False),
        test_count=443,
    )

    assert progress.status == "in_progress"


def test_git_intelligence_progress_ready_for_closeout_when_capabilities_and_endpoints_complete():
    progress = GitIntelligenceProgressBuilder().build(make_report(), test_count=443)

    assert progress.capability_count >= 5
    assert progress.endpoint_count == 5
    assert progress.ready_for_closeout is True


def test_git_intelligence_progress_not_ready_when_status_in_progress():
    progress = GitIntelligenceProgressBuilder().build(
        make_report(is_repository=False, current_branch=None, commits=False, authors=False),
        test_count=443,
    )

    assert progress.ready_for_closeout is False


def test_git_intelligence_progress_counts_missing_branch_as_lower_capability():
    progress = GitIntelligenceProgressBuilder().build(
        make_report(current_branch=None),
        test_count=443,
    )

    assert progress.capability_count == 4
