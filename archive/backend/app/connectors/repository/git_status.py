from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.connectors.repository.git_command import GitCommandRunner


@dataclass(frozen=True)
class GitStatusEntry:
    status: str
    path: str


@dataclass(frozen=True)
class GitStatusReport:
    entries: list[GitStatusEntry]

    @property
    def is_clean(self) -> bool:
        return len(self.entries) == 0

    @property
    def modified_count(self) -> int:
        return sum(1 for entry in self.entries if "M" in entry.status)

    @property
    def untracked_count(self) -> int:
        return sum(1 for entry in self.entries if "??" in entry.status)


class GitStatusReader:
    def __init__(self, runner: GitCommandRunner | None = None):
        self.runner = runner or GitCommandRunner()

    def status(self, repository_path: str | Path) -> GitStatusReport:
        result = self.runner.run(repository_path, ["status", "--short"])

        if not result.ok:
            raise RuntimeError(result.stderr.strip() or "Unable to read git status.")

        entries = []

        for line in result.stdout.splitlines():
            if not line.strip():
                continue

            entries.append(
                GitStatusEntry(
                    status=line[:2].strip(),
                    path=line[3:].strip(),
                )
            )

        return GitStatusReport(entries=entries)
