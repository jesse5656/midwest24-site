from __future__ import annotations

from pathlib import Path

from app.connectors.repository.git_command import GitCommandRunner


class GitRepositoryDetector:
    def __init__(self, runner: GitCommandRunner | None = None):
        self.runner = runner or GitCommandRunner()

    def is_git_repository(self, repository_path: str | Path) -> bool:
        repository_path = Path(repository_path).expanduser().resolve()

        if not repository_path.exists() or not repository_path.is_dir():
            return False

        result = self.runner.run(repository_path, ["rev-parse", "--is-inside-work-tree"])

        return result.ok and result.stdout.strip() == "true"

    def repository_root(self, repository_path: str | Path) -> Path | None:
        repository_path = Path(repository_path).expanduser().resolve()

        if not repository_path.exists() or not repository_path.is_dir():
            return None

        result = self.runner.run(repository_path, ["rev-parse", "--show-toplevel"])

        if not result.ok:
            return None

        return Path(result.stdout.strip()).resolve()

    def current_branch(self, repository_path: str | Path) -> str | None:
        result = self.runner.run(repository_path, ["branch", "--show-current"])

        if not result.ok:
            return None

        branch = result.stdout.strip()

        return branch or None
