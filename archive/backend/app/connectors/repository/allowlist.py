from __future__ import annotations

from pathlib import Path


class RepositoryAllowlist:
    """
    Enforces allowed repository roots for local repository ingestion.

    An empty root list means no allowlist is configured and validation is skipped.
    """

    def __init__(self, roots: list[str | Path] | None = None):
        self.roots = [
            Path(root).expanduser().resolve()
            for root in (roots or [])
            if str(root).strip()
        ]

    def validate(self, repository_path: str | Path) -> Path:
        repository_path = Path(repository_path).expanduser().resolve()

        if not self.roots:
            return repository_path

        if any(repository_path == root or root in repository_path.parents for root in self.roots):
            return repository_path

        raise PermissionError(
            f"Repository path is outside configured allowed roots: {repository_path}"
        )
