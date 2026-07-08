from pathlib import Path

from fastapi.testclient import TestClient

from app.connectors.repository import ArchiveRepositoryIngestor
from app.db.session import SessionLocal
from app.main import app
from app.models.entity import Entity

client = TestClient(app)


def test_archive_repository_ingestor_reports_skipped_and_unsupported_files(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    db = SessionLocal()

    try:
        entity = Entity(title="Discovery Observable Repository", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()

        (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")
        (repo / "image.png").write_bytes(b"skip")

        cache_dir = repo / ".cache"
        cache_dir.mkdir()
        (cache_dir / "cache.txt").write_text("skip cache\n", encoding="utf-8")

        report = ArchiveRepositoryIngestor(db).ingest_repository(
            entity_id=entity.id,
            repository_path=repo,
        )

        assert report.discovered_count == 1
        assert report.document_count == 1
        assert report.processing_job_count == 1
        assert report.skipped_count == 1
        assert report.unsupported_count == 1
        assert report.skipped_paths[0].path == ".cache"
        assert report.unsupported_files[0].path == "image.png"

    finally:
        db.close()


def test_repository_ingestion_api_reports_skipped_and_unsupported_files(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity_response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "repository",
            "title": "Discovery Observable Repository API",
        },
    )
    assert entity_response.status_code == 201
    entity = entity_response.json()

    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")
    (repo / "photo.jpg").write_bytes(b"skip")

    git_dir = repo / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\n", encoding="utf-8")

    response = client.post(
        "/api/v1/repository-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["discovered_count"] == 1
    assert data["document_count"] == 1
    assert data["processing_job_count"] == 1
    assert data["skipped_count"] == 1
    assert data["unsupported_count"] == 1
    assert data["skipped_paths"][0]["path"] == ".git"
    assert data["unsupported_files"][0]["path"] == "photo.jpg"
    assert data["unsupported_files"][0]["suffix"] == ".jpg"
