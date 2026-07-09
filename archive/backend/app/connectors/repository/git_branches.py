from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.connectors.repository.git_command import GitCommandRunner


@dataclass(frozen=True)
class GitBranch:
    name: str
    current: bool = False


class GitBranchReader:
    def __init__(self, runner: GitCommandRunner | None = None):
        self.runner = runner or GitCommandRunner()

    def branches(self, repository_path: str | Path) -> list[GitBranch]:
        result = self.runner.run(repository_path, ["branch", "--format=%(HEAD)%x1f%(refname:short)"])

        if not result.ok:
            raise RuntimeError(result.stderr.strip() or "Unable to read git branches.")

        branches = []

        for line in result.stdout.splitlines():
            if not line.strip():
                continue

            marker, name = line.split("\x1f", 1)
            branches.append(GitBranch(name=name.strip(), current=marker.strip() == "*"))

        return branches

    def current_branch(self, repository_path: str | Path) -> GitBranch | None:
        for branch in self.branches(repository_path):
            if branch.current:
                return branch

        return None
