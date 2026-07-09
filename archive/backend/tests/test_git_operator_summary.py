from app.connectors.repository import GitRepositoryOperatorSummaryBuilder, GitRepositorySummary


def test_git_operator_summary_reports_not_git_repository():
    summary = GitRepositorySummary(
        is_repository=False,
        root=None,
        current_branch=None,
        recent_commit_count=0,
        is_clean=None,
    )

    result = GitRepositoryOperatorSummaryBuilder().build(summary)

    assert result.outcome == "not_git_repository"
    assert result.action_required is True
    assert "not a Git repository" in result.message


def test_git_operator_summary_reports_detached_or_unknown_branch():
    summary = GitRepositorySummary(
        is_repository=True,
        root="/repo",
        current_branch=None,
        recent_commit_count=1,
        is_clean=True,
    )

    result = GitRepositoryOperatorSummaryBuilder().build(summary)

    assert result.outcome == "detached_or_unknown_branch"
    assert result.action_required is False
    assert "no current branch" in result.message


def test_git_operator_summary_reports_repository_has_changes():
    summary = GitRepositorySummary(
        is_repository=True,
        root="/repo",
        current_branch="main",
        recent_commit_count=2,
        is_clean=False,
    )

    result = GitRepositoryOperatorSummaryBuilder().build(summary)

    assert result.outcome == "repository_has_changes"
    assert result.action_required is False
    assert "uncommitted changes" in result.message


def test_git_operator_summary_reports_clean_repository():
    summary = GitRepositorySummary(
        is_repository=True,
        root="/repo",
        current_branch="main",
        recent_commit_count=3,
        is_clean=True,
    )

    result = GitRepositoryOperatorSummaryBuilder().build(summary)

    assert result.outcome == "repository_clean"
    assert result.action_required is False
    assert "3 recent commit" in result.message


def test_git_operator_summary_clean_message_includes_branch():
    summary = GitRepositorySummary(
        is_repository=True,
        root="/repo",
        current_branch="feature",
        recent_commit_count=1,
        is_clean=True,
    )

    result = GitRepositoryOperatorSummaryBuilder().build(summary)

    assert "feature" in result.message


def test_git_operator_summary_dirty_message_includes_branch():
    summary = GitRepositorySummary(
        is_repository=True,
        root="/repo",
        current_branch="dev",
        recent_commit_count=1,
        is_clean=False,
    )

    result = GitRepositoryOperatorSummaryBuilder().build(summary)

    assert "dev" in result.message
