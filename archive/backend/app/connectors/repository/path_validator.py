from __future__ import annotations

from pathlib import Path


class RepositoryPathValidator:
    """
    Validates repository paths before Archive ingestion.

    Policy:
    - Path must exist.
    - Path must be a directory.
    - Path must not be a symbolic link.
    - Repository directory name must not be hidden.
    """

    @staticmethod
    def validate(path: str | Path) -> Path:
        raw_path = Path(path).expanduser()

        if raw_path.is_symlink():
            raise ValueError("Repository path symbolic links are not permitted.")

        resolved_path = raw_path.resolve()

        if not resolved_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {resolved_path}")

        if not resolved_path.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {resolved_path}")

        if resolved_path.name.startswith("."):
            raise ValueError("Hidden repository directories are not permitted.")

        return resolved_path
