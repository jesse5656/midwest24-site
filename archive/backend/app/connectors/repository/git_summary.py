from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.connectors.repository.git_branches import GitBranchReader
from app.connectors.repository.git_history import GitHistoryReader
from app.connectors.repository.git_repository import GitRepositoryDetector
from app.connectors.repository.git_status import GitStatusReader


@dataclass(frozen=True)
class GitRepositorySummary:
    is_repository: bool
    root: str | None
    current_branch: str | None
    recent_commit_count: int
    is_clean: bool | None


class GitRepositorySummaryBuilder:
    def __init__(
        self,
        detector: GitRepositoryDetector | None = None,
        branch_reader: GitBranchReader | None = None,
        history_reader: GitHistoryReader | None = None,
        status_reader: GitStatusReader | None = None,
    ):
        self.detector = detector or GitRepositoryDetector()
        self.branch_reader = branch_reader or GitBranchReader()
        self.history_reader = history_reader or GitHistoryReader()
        self.status_reader = status_reader or GitStatusReader()

    def build(self, repository_path: str | Path, commit_limit: int = 5) -> GitRepositorySummary:
        if not self.detector.is_git_repository(repository_path):
            return GitRepositorySummary(
                is_repository=False,
                root=None,
                current_branch=None,
                recent_commit_count=0,
                is_clean=None,
            )

        root = self.detector.repository_root(repository_path)
        current_branch = self.branch_reader.current_branch(repository_path)
        commits = self.history_reader.recent_commits(repository_path, limit=commit_limit)
        status = self.status_reader.status(repository_path)

        return GitRepositorySummary(
            is_repository=True,
            root=str(root) if root else None,
            current_branch=current_branch.name if current_branch else None,
            recent_commit_count=len(commits),
            is_clean=status.is_clean,
        )
