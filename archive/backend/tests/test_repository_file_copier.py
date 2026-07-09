from pathlib import Path

from app.connectors.repository import RepositoryFileCopier


def test_repository_file_copier_copies_file_contents(tmp_path: Path):
    source = tmp_path / "source.md"
    destination = tmp_path / "destination.md"

    source.write_text("# Copied\n", encoding="utf-8")

    RepositoryFileCopier().copy(source, destination)

    assert destination.read_text(encoding="utf-8") == "# Copied\n"


def test_repository_file_copier_overwrites_existing_destination(tmp_path: Path):
    source = tmp_path / "source.md"
    destination = tmp_path / "destination.md"

    source.write_text("new content\n", encoding="utf-8")
    destination.write_text("old content\n", encoding="utf-8")

    RepositoryFileCopier().copy(source, destination)

    assert destination.read_text(encoding="utf-8") == "new content\n"


def test_repository_file_copier_raises_for_missing_source(tmp_path: Path):
    source = tmp_path / "missing.md"
    destination = tmp_path / "destination.md"

    try:
        RepositoryFileCopier().copy(source, destination)
    except FileNotFoundError:
        assert not destination.exists()
    else:
        raise AssertionError("Expected FileNotFoundError")
