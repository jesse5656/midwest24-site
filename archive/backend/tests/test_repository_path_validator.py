from pathlib import Path

import pytest

from app.connectors.repository.path_validator import RepositoryPathValidator


def test_accepts_normal_repository(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    validated = RepositoryPathValidator.validate(repo)

    assert validated == repo.resolve()


def test_rejects_missing_repository(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        RepositoryPathValidator.validate(tmp_path / "missing")


def test_rejects_file(tmp_path: Path):
    f = tmp_path / "README.md"
    f.write_text("hello")

    with pytest.raises(NotADirectoryError):
        RepositoryPathValidator.validate(f)


def test_rejects_hidden_directory(tmp_path: Path):
    repo = tmp_path / ".secret"
    repo.mkdir()

    with pytest.raises(ValueError):
        RepositoryPathValidator.validate(repo)
