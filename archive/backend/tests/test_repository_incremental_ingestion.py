from pathlib import Path

from sqlalchemy import select

from app.connectors.repository import RepositoryIncrementalIngestor, RepositoryManifestStore
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.entity import Entity


def create_entity(db, title="Incremental Repository"):
    entity = Entity(title=title, entity_type="repository")
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def test_incremental_ingestor_ingests_new_files_and_saves_manifest(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# New\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"

    db = SessionLocal()
    try:
        entity = create_entity(db)

        result = RepositoryIncrementalIngestor(
            db,
            RepositoryManifestStore(manifest_path),
        ).ingest_changed_repository(entity.id, repo)

        assert result.new_count == 1
        assert result.modified_count == 0
        assert result.deleted_count == 0
        assert result.ingested_document_count == 1
        assert result.processing_job_count == 1
        assert result.manifest_updated is True
        assert manifest_path.exists()

    finally:
        db.close()


def test_incremental_ingestor_skips_ingestion_when_repository_unchanged(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Stable\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"

    db = SessionLocal()
    try:
        entity = create_entity(db, "Stable Repository")
        ingestor = RepositoryIncrementalIngestor(db, RepositoryManifestStore(manifest_path))

        first = ingestor.ingest_changed_repository(entity.id, repo)
        second = ingestor.ingest_changed_repository(entity.id, repo)

        assert first.new_count == 1
        assert second.changed_count == 0
        assert second.ingestion_report is None
        assert second.ingested_document_count == 0
        assert second.processing_job_count == 0

    finally:
        db.close()


def test_incremental_ingestor_reports_modified_files(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# First\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"

    db = SessionLocal()
    try:
        entity = create_entity(db, "Modified Repository")
        ingestor = RepositoryIncrementalIngestor(db, RepositoryManifestStore(manifest_path))

        ingestor.ingest_changed_repository(entity.id, repo)
        (repo / "README.md").write_text("# Second\n", encoding="utf-8")

        result = ingestor.ingest_changed_repository(entity.id, repo)

        assert result.new_count == 0
        assert result.modified_count == 1
        assert result.changes.modified_files == ["README.md"]
        assert result.ingested_document_count == 0

    finally:
        db.close()


def test_incremental_ingestor_reports_deleted_files_and_updates_manifest(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    repo = tmp_path / "repo"
    repo.mkdir()
    readme = repo / "README.md"
    readme.write_text("# Delete Me\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"

    db = SessionLocal()
    try:
        entity = create_entity(db, "Deleted Repository")
        ingestor = RepositoryIncrementalIngestor(db, RepositoryManifestStore(manifest_path))

        ingestor.ingest_changed_repository(entity.id, repo)
        readme.unlink()

        result = ingestor.ingest_changed_repository(entity.id, repo)
        saved = RepositoryManifestStore(manifest_path).load()

        assert result.deleted_count == 1
        assert result.changes.deleted_files == ["README.md"]
        assert saved.paths() == set()

    finally:
        db.close()


def test_incremental_ingestor_only_copies_changed_files_into_temp_ingestion(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "A.md").write_text("# A1\n", encoding="utf-8")
    (repo / "B.md").write_text("# B1\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"

    db = SessionLocal()
    try:
        entity = create_entity(db, "Changed Only Repository")
        ingestor = RepositoryIncrementalIngestor(db, RepositoryManifestStore(manifest_path))

        ingestor.ingest_changed_repository(entity.id, repo)
        (repo / "A.md").write_text("# A2\n", encoding="utf-8")

        result = ingestor.ingest_changed_repository(entity.id, repo)

        assert result.modified_count == 1
        assert result.changes.unchanged_files == ["B.md"]

        documents = list(
            db.execute(
                select(Document)
                .where(Document.entity_id == entity.id)
                .order_by(Document.filename.asc())
            ).scalars()
        )

        assert [document.filename for document in documents] == ["A.md", "B.md"]

    finally:
        db.close()
