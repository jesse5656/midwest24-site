from pathlib import Path

from app.connectors.repository import (
    REPOSITORY_ALLOWED_ROOTS_ENV,
    get_repository_allowed_roots,
)


def test_repository_allowed_roots_defaults_to_empty(monkeypatch):
    monkeypatch.delenv(REPOSITORY_ALLOWED_ROOTS_ENV, raising=False)

    assert get_repository_allowed_roots() == []


def test_repository_allowed_roots_reads_colon_separated_paths(tmp_path: Path, monkeypatch):
    first = tmp_path / "first"
    second = tmp_path / "second"

    monkeypatch.setenv(
        REPOSITORY_ALLOWED_ROOTS_ENV,
        f"{first}:{second}",
    )

    assert get_repository_allowed_roots() == [
        first.resolve(),
        second.resolve(),
    ]
