from pathlib import Path

from app.connectors.repository import ArchiveRepositoryIngestor, RepositoryFile
from app.db.session import SessionLocal


def make_repository_file(tmp_path: Path, name: str):
    path = tmp_path / name
    path.write_text("content", encoding="utf-8")
    return RepositoryFile(
        path=path,
        relative_path=name,
        suffix=path.suffix,
        size_bytes=path.stat().st_size,
    )


def test_repository_ingestor_guesses_markdown_mime_type(tmp_path: Path):
    db = SessionLocal()
    try:
        file = make_repository_file(tmp_path, "README.md")
        assert ArchiveRepositoryIngestor(db)._guess_mime_type(file) == "text/markdown"
    finally:
        db.close()


def test_repository_ingestor_guesses_json_mime_type(tmp_path: Path):
    db = SessionLocal()
    try:
        file = make_repository_file(tmp_path, "data.json")
        assert ArchiveRepositoryIngestor(db)._guess_mime_type(file) == "application/json"
    finally:
        db.close()


def test_repository_ingestor_guesses_yaml_mime_type(tmp_path: Path):
    db = SessionLocal()
    try:
        file = make_repository_file(tmp_path, "config.yaml")
        assert ArchiveRepositoryIngestor(db)._guess_mime_type(file) == "application/x-yaml"
    finally:
        db.close()


def test_repository_ingestor_guesses_code_mime_type_as_plain_text(tmp_path: Path):
    db = SessionLocal()
    try:
        file = make_repository_file(tmp_path, "script.py")
        assert ArchiveRepositoryIngestor(db)._guess_mime_type(file) == "text/plain"
    finally:
        db.close()


def test_repository_ingestor_guesses_unknown_mime_type_as_octet_stream(tmp_path: Path):
    db = SessionLocal()
    try:
        file = make_repository_file(tmp_path, "archive.unknown")
        assert ArchiveRepositoryIngestor(db)._guess_mime_type(file) == "application/octet-stream"
    finally:
        db.close()
