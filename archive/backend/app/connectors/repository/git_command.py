from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitCommandResult:
    command: list[str]
    cwd: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class GitCommandRunner:
    def run(self, repository_path: str | Path, args: list[str]) -> GitCommandResult:
        repository_path = Path(repository_path).expanduser().resolve()
        command = ["git", *args]

        completed = subprocess.run(
            command,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=False,
        )

        return GitCommandResult(
            command=command,
            cwd=str(repository_path),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
