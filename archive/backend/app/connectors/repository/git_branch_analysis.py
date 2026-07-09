from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.git_branches import GitBranch, GitBranchReader


@dataclass(frozen=True)
class GitBranchAnalysis:
    branches: list[GitBranch] = field(default_factory=list)

    @property
    def branch_count(self) -> int:
        return len(self.branches)

    @property
    def current_branch(self) -> GitBranch | None:
        for branch in self.branches:
            if branch.current:
                return branch
        return None

    @property
    def current_branch_name(self) -> str | None:
        if self.current_branch is None:
            return None
        return self.current_branch.name

    @property
    def has_multiple_branches(self) -> bool:
        return self.branch_count > 1

    @property
    def branch_names(self) -> list[str]:
        return [branch.name for branch in self.branches]

    @property
    def non_current_branch_names(self) -> list[str]:
        return [branch.name for branch in self.branches if not branch.current]


class GitBranchAnalysisBuilder:
    def __init__(self, branch_reader: GitBranchReader | None = None):
        self.branch_reader = branch_reader or GitBranchReader()

    def build(self, repository_path: str | Path) -> GitBranchAnalysis:
        return GitBranchAnalysis(branches=self.branch_reader.branches(repository_path))
