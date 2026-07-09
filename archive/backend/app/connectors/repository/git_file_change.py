from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.git_command import GitCommandRunner


@dataclass(frozen=True)
class GitFileChange:
    status: str
    path: str

    @property
    def is_added(self) -> bool:
        return self.status == "A"

    @property
    def is_modified(self) -> bool:
        return self.status == "M"

    @property
    def is_deleted(self) -> bool:
        return self.status == "D"

    @property
    def is_renamed(self) -> bool:
        return self.status.startswith("R")


@dataclass(frozen=True)
class GitCommitFileChangeSet:
    commit_sha: str
    short_sha: str
    subject: str
    files: list[GitFileChange] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def added_count(self) -> int:
        return sum(1 for file in self.files if file.is_added)

    @property
    def modified_count(self) -> int:
        return sum(1 for file in self.files if file.is_modified)

    @property
    def deleted_count(self) -> int:
        return sum(1 for file in self.files if file.is_deleted)

    @property
    def renamed_count(self) -> int:
        return sum(1 for file in self.files if file.is_renamed)


@dataclass(frozen=True)
class GitFileChangePreview:
    commits: list[GitCommitFileChangeSet] = field(default_factory=list)

    @property
    def commit_count(self) -> int:
        return len(self.commits)

    @property
    def file_change_count(self) -> int:
        return sum(commit.file_count for commit in self.commits)

    @property
    def added_count(self) -> int:
        return sum(commit.added_count for commit in self.commits)

    @property
    def modified_count(self) -> int:
        return sum(commit.modified_count for commit in self.commits)

    @property
    def deleted_count(self) -> int:
        return sum(commit.deleted_count for commit in self.commits)

    @property
    def renamed_count(self) -> int:
        return sum(commit.renamed_count for commit in self.commits)

    @property
    def touched_paths(self) -> list[str]:
        return sorted({file.path for commit in self.commits for file in commit.files})


class GitFileChangeParser:
    COMMIT_SEPARATOR = "\x1e"
    FIELD_SEPARATOR = "\x1f"

    def parse(self, text: str) -> GitFileChangePreview:
        commits: list[GitCommitFileChangeSet] = []

        for raw_block in text.split(self.COMMIT_SEPARATOR):
            block = raw_block.strip("\n")
            if not block.strip():
                continue

            lines = [line for line in block.splitlines() if line.strip()]
            header = lines[0].split(self.FIELD_SEPARATOR)

            if len(header) != 3:
                raise ValueError(f"Invalid git file-change commit header: {lines[0]!r}")

            sha, short_sha, subject = header
            files = [self.parse_file_line(line) for line in lines[1:]]

            commits.append(
                GitCommitFileChangeSet(
                    commit_sha=sha,
                    short_sha=short_sha,
                    subject=subject,
                    files=files,
                )
            )

        return GitFileChangePreview(commits=commits)

    def parse_file_line(self, line: str) -> GitFileChange:
        parts = line.split("\t")

        if len(parts) < 2:
            raise ValueError(f"Invalid git file-change line: {line!r}")

        status = parts[0]
        path = parts[-1]

        return GitFileChange(status=status, path=path)


class GitFileChangePreviewBuilder:
    def __init__(
        self,
        runner: GitCommandRunner | None = None,
        parser: GitFileChangeParser | None = None,
    ):
        self.runner = runner or GitCommandRunner()
        self.parser = parser or GitFileChangeParser()

    def build(self, repository_path: str | Path, limit: int = 10) -> GitFileChangePreview:
        if limit < 1:
            raise ValueError("File-change preview limit must be at least 1.")

        result = self.runner.run(
            repository_path,
            [
                "log",
                f"--max-count={limit}",
                "--pretty=format:%x1e%H%x1f%h%x1f%s",
                "--name-status",
            ],
        )

        if not result.ok:
            raise RuntimeError(result.stderr.strip() or "Unable to read git file changes.")

        return self.parser.parse(result.stdout)
