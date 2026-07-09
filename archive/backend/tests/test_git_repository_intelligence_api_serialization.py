from app.api.git_repository_intelligence import (
    serialize_git_operator_summary,
    serialize_git_repository_summary,
)
from app.connectors.repository import GitRepositorySummary


def test_serialize_git_repository_summary_for_repository():
    summary = GitRepositorySummary(
        is_repository=True,
        root="/repo",
        current_branch="main",
        recent_commit_count=4,
        is_clean=True,
    )

    response = serialize_git_repository_summary(summary)

    assert response.is_repository is True
    assert response.root == "/repo"
    assert response.current_branch == "main"
    assert response.recent_commit_count == 4
    assert response.is_clean is True


def test_serialize_git_repository_summary_for_non_repository():
    summary = GitRepositorySummary(
        is_repository=False,
        root=None,
        current_branch=None,
        recent_commit_count=0,
        is_clean=None,
    )

    response = serialize_git_repository_summary(summary)

    assert response.is_repository is False
    assert response.root is None
    assert response.current_branch is None
    assert response.is_clean is None


def test_serialize_git_operator_summary_for_clean_repository():
    summary = GitRepositorySummary(
        is_repository=True,
        root="/repo",
        current_branch="main",
        recent_commit_count=2,
        is_clean=True,
    )

    response = serialize_git_operator_summary(summary)

    assert response.outcome == "repository_clean"
    assert response.action_required is False


def test_serialize_git_operator_summary_for_dirty_repository():
    summary = GitRepositorySummary(
        is_repository=True,
        root="/repo",
        current_branch="main",
        recent_commit_count=2,
        is_clean=False,
    )

    response = serialize_git_operator_summary(summary)

    assert response.outcome == "repository_has_changes"
    assert response.action_required is False


def test_serialize_git_operator_summary_for_non_repository():
    summary = GitRepositorySummary(
        is_repository=False,
        root=None,
        current_branch=None,
        recent_commit_count=0,
        is_clean=None,
    )

    response = serialize_git_operator_summary(summary)

    assert response.outcome == "not_git_repository"
    assert response.action_required is True
