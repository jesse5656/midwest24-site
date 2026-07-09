from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GitCommit:
    sha: str
    short_sha: str
    author_name: str
    author_email: str
    authored_at: str
    subject: str

    @property
    def display(self) -> str:
        return f"{self.short_sha} {self.subject}"


class GitCommitParser:
    FIELD_SEPARATOR = "\x1f"

    def parse_line(self, line: str) -> GitCommit:
        parts = line.rstrip("\n").split(self.FIELD_SEPARATOR)

        if len(parts) != 6:
            raise ValueError(f"Invalid git commit line: {line!r}")

        sha, short_sha, author_name, author_email, authored_at, subject = parts

        return GitCommit(
            sha=sha,
            short_sha=short_sha,
            author_name=author_name,
            author_email=author_email,
            authored_at=authored_at,
            subject=subject,
        )

    def parse_lines(self, text: str) -> list[GitCommit]:
        return [
            self.parse_line(line)
            for line in text.splitlines()
            if line.strip()
        ]
