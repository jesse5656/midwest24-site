import logging
from pathlib import Path

from app.connectors.repository import ArchiveRepositoryIngestor
from app.db.session import SessionLocal
from app.models.entity import Entity


class FailingFileCopier:
    def copy(self, source_path, destination_path):
        raise RuntimeError("logging copy failure")


def test_repository_ingestion_logs_start_and_finish(tmp_path: Path, monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    db = SessionLocal()
    try:
        entity = Entity(title="Logging Repository", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()
        (repo / "README.md").write_text("# Logging\n", encoding="utf-8")

        ArchiveRepositoryIngestor(db).ingest_repository(entity.id, repo)

        messages = [record.getMessage() for record in caplog.records]

        assert "Repository ingestion started" in messages
        assert "Repository ingestion finished" in messages

    finally:
        db.close()


def test_repository_ingestion_logs_file_failure(tmp_path: Path, monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    db = SessionLocal()
    try:
        entity = Entity(title="Failure Logging Repository", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()
        (repo / "README.md").write_text("# Logging Failure\n", encoding="utf-8")

        ArchiveRepositoryIngestor(
            db,
            file_copier=FailingFileCopier(),
        ).ingest_repository(entity.id, repo)

        messages = [record.getMessage() for record in caplog.records]

        assert "Repository file ingestion failed" in messages
        assert "Repository ingestion finished" in messages

    finally:
        db.close()


def test_repository_ingestion_finish_log_includes_failure_count(
    tmp_path: Path,
    monkeypatch,
    caplog,
):
    caplog.set_level(logging.INFO)

    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    db = SessionLocal()
    try:
        entity = Entity(title="Failure Count Logging Repository", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()
        (repo / "README.md").write_text("# Logging Failure Count\n", encoding="utf-8")

        ArchiveRepositoryIngestor(
            db,
            file_copier=FailingFileCopier(),
        ).ingest_repository(entity.id, repo)

        finish_records = [
            record for record in caplog.records
            if record.getMessage() == "Repository ingestion finished"
        ]

        assert len(finish_records) >= 1
        assert getattr(finish_records[-1], "failure_count") == 1

    finally:
        db.close()
