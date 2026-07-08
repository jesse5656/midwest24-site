from pathlib import Path

import pytest

from app.connectors.repository import RepositoryPathValidator


def test_repository_path_validator_accepts_normal_directory(tmp_path: Path):
    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    assert RepositoryPathValidator.validate(repo) == repo.resolve()


def test_repository_path_validator_rejects_missing_path(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        RepositoryPathValidator.validate(tmp_path / "missing-repo")


def test_repository_path_validator_rejects_file_path(tmp_path: Path):
    file_path = tmp_path / "README.md"
    file_path.write_text("# Not a directory\n", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        RepositoryPathValidator.validate(file_path)


def test_repository_path_validator_rejects_hidden_repository_directory(tmp_path: Path):
    repo = tmp_path / ".hidden-repo"
    repo.mkdir()

    with pytest.raises(ValueError):
        RepositoryPathValidator.validate(repo)


def test_repository_path_validator_rejects_symbolic_link(tmp_path: Path):
    target = tmp_path / "target-repo"
    target.mkdir()

    symlink = tmp_path / "linked-repo"
    symlink.symlink_to(target, target_is_directory=True)

    with pytest.raises(ValueError):
        RepositoryPathValidator.validate(symlink)
