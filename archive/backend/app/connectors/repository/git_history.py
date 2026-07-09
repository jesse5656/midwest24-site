from __future__ import annotations

from pathlib import Path

from app.connectors.repository.git_command import GitCommandRunner
from app.connectors.repository.git_commit import GitCommit, GitCommitParser


class GitHistoryReader:
    def __init__(
        self,
        runner: GitCommandRunner | None = None,
        parser: GitCommitParser | None = None,
    ):
        self.runner = runner or GitCommandRunner()
        self.parser = parser or GitCommitParser()

    def recent_commits(self, repository_path: str | Path, limit: int = 10) -> list[GitCommit]:
        if limit < 1:
            raise ValueError("Commit limit must be at least 1.")

        result = self.runner.run(
            repository_path,
            [
                "log",
                f"--max-count={limit}",
                "--pretty=format:%H%x1f%h%x1f%an%x1f%ae%x1f%aI%x1f%s",
            ],
        )

        if not result.ok:
            raise RuntimeError(result.stderr.strip() or "Unable to read git history.")

        return self.parser.parse_lines(result.stdout)
