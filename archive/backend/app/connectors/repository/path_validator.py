from pathlib import Path


class RepositoryPathValidator:
    """
    Validates repository paths before Archive ingestion.

    Current policy:

    - Path must exist.
    - Path must be a directory.
    - Symbolic links are rejected.
    - Hidden directories are rejected.
    """

    @staticmethod
    def validate(path: str | Path) -> Path:
        path = Path(path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(path)

        if not path.is_dir():
            raise NotADirectoryError(path)

        if path.is_symlink():
            raise ValueError("Symbolic links are not permitted.")

        if path.name.startswith("."):
            raise ValueError("Hidden repositories are not permitted.")

        return path
