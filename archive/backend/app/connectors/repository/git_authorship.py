from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.git_commit import GitCommit
from app.connectors.repository.git_history import GitHistoryReader


@dataclass(frozen=True)
class GitAuthorSummary:
    author_name: str
    author_email: str
    commit_count: int
    first_authored_at: str
    last_authored_at: str

    @property
    def identity(self) -> str:
        return f"{self.author_name} <{self.author_email}>"


@dataclass(frozen=True)
class GitAuthorshipPreview:
    commits: list[GitCommit] = field(default_factory=list)

    @property
    def commit_count(self) -> int:
        return len(self.commits)

    @property
    def authors(self) -> list[GitAuthorSummary]:
        grouped: dict[tuple[str, str], list[GitCommit]] = {}

        for commit in self.commits:
            key = (commit.author_name, commit.author_email)
            grouped.setdefault(key, []).append(commit)

        authors = []

        for (name, email), commits in grouped.items():
            authored_dates = sorted(commit.authored_at for commit in commits)
            authors.append(
                GitAuthorSummary(
                    author_name=name,
                    author_email=email,
                    commit_count=len(commits),
                    first_authored_at=authored_dates[0],
                    last_authored_at=authored_dates[-1],
                )
            )

        return sorted(
            authors,
            key=lambda author: (
                -author.commit_count,
                author.author_name.lower(),
                author.author_email.lower(),
            ),
        )

    @property
    def author_count(self) -> int:
        return len(self.authors)

    @property
    def top_author(self) -> GitAuthorSummary | None:
        if not self.authors:
            return None
        return self.authors[0]

    @property
    def first_authored_at(self) -> str | None:
        if not self.commits:
            return None
        return min(commit.authored_at for commit in self.commits)

    @property
    def last_authored_at(self) -> str | None:
        if not self.commits:
            return None
        return max(commit.authored_at for commit in self.commits)


class GitAuthorshipPreviewBuilder:
    def __init__(self, history_reader: GitHistoryReader | None = None):
        self.history_reader = history_reader or GitHistoryReader()

    def build(self, repository_path: str | Path, limit: int = 50) -> GitAuthorshipPreview:
        commits = self.history_reader.recent_commits(repository_path, limit=limit)
        return GitAuthorshipPreview(commits=commits)
