from pathlib import Path

import pytest

from app.connectors.repository import RepositoryAllowlist


def test_repository_allowlist_allows_any_path_when_unconfigured(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    assert RepositoryAllowlist().validate(repo) == repo.resolve()


def test_repository_allowlist_accepts_configured_root(tmp_path: Path):
    allowed_root = tmp_path / "repositories"
    allowed_root.mkdir()

    assert RepositoryAllowlist([allowed_root]).validate(allowed_root) == allowed_root.resolve()


def test_repository_allowlist_accepts_child_of_configured_root(tmp_path: Path):
    allowed_root = tmp_path / "repositories"
    allowed_root.mkdir()

    repo = allowed_root / "knowledge-repo"
    repo.mkdir()

    assert RepositoryAllowlist([allowed_root]).validate(repo) == repo.resolve()


def test_repository_allowlist_rejects_path_outside_configured_root(tmp_path: Path):
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()

    outside = tmp_path / "outside"
    outside.mkdir()

    with pytest.raises(PermissionError):
        RepositoryAllowlist([allowed_root]).validate(outside)
