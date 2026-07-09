from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.git_commit import GitCommit
from app.connectors.repository.git_history import GitHistoryReader


@dataclass(frozen=True)
class GitAuthorContribution:
    author_name: str
    author_email: str
    commit_count: int


@dataclass(frozen=True)
class GitCommitPreview:
    commits: list[GitCommit] = field(default_factory=list)

    @property
    def commit_count(self) -> int:
        return len(self.commits)

    @property
    def authors(self) -> list[GitAuthorContribution]:
        counts: dict[tuple[str, str], int] = {}

        for commit in self.commits:
            key = (commit.author_name, commit.author_email)
            counts[key] = counts.get(key, 0) + 1

        return [
            GitAuthorContribution(
                author_name=name,
                author_email=email,
                commit_count=count,
            )
            for (name, email), count in sorted(
                counts.items(),
                key=lambda item: (-item[1], item[0][0].lower(), item[0][1].lower()),
            )
        ]

    @property
    def latest_commit(self) -> GitCommit | None:
        if not self.commits:
            return None
        return self.commits[0]

    @property
    def oldest_commit(self) -> GitCommit | None:
        if not self.commits:
            return None
        return self.commits[-1]


class GitCommitPreviewBuilder:
    def __init__(self, history_reader: GitHistoryReader | None = None):
        self.history_reader = history_reader or GitHistoryReader()

    def build(self, repository_path: str | Path, limit: int = 10) -> GitCommitPreview:
        commits = self.history_reader.recent_commits(repository_path, limit=limit)
        return GitCommitPreview(commits=commits)
