from pathlib import Path

from app.connectors.repository import (
    GitBranch,
    GitCommit,
    GitRepositorySummaryBuilder,
    GitStatusReport,
)


class FakeDetector:
    def __init__(self, is_repo=True, root="/repo"):
        self.is_repo = is_repo
        self.root = root

    def is_git_repository(self, repository_path):
        return self.is_repo

    def repository_root(self, repository_path):
        return Path(self.root)


class FakeBranchReader:
    def __init__(self, branch=None):
        self.branch = branch

    def current_branch(self, repository_path):
        if self.branch is None:
            return None
        return GitBranch(name=self.branch, current=True)


class FakeHistoryReader:
    def __init__(self, count=2):
        self.count = count

    def recent_commits(self, repository_path, limit=5):
        return [
            GitCommit(
                sha=str(index),
                short_sha=str(index),
                author_name="A",
                author_email="a@example.com",
                authored_at="2026-01-01T00:00:00Z",
                subject="Subject",
            )
            for index in range(self.count)
        ]


class FakeStatusReader:
    def __init__(self, clean=True):
        self.clean = clean

    def status(self, repository_path):
        return GitStatusReport(entries=[] if self.clean else [])


def test_git_summary_reports_non_repository():
    summary = GitRepositorySummaryBuilder(
        detector=FakeDetector(is_repo=False),
    ).build("/repo")

    assert summary.is_repository is False
    assert summary.root is None
    assert summary.current_branch is None
    assert summary.recent_commit_count == 0
    assert summary.is_clean is None


def test_git_summary_reports_repository_metadata():
    summary = GitRepositorySummaryBuilder(
        detector=FakeDetector(is_repo=True, root="/repo"),
        branch_reader=FakeBranchReader(branch="main"),
        history_reader=FakeHistoryReader(count=3),
        status_reader=FakeStatusReader(clean=True),
    ).build("/repo", commit_limit=3)

    assert summary.is_repository is True
    assert summary.root == "/repo"
    assert summary.current_branch == "main"
    assert summary.recent_commit_count == 3
    assert summary.is_clean is True
