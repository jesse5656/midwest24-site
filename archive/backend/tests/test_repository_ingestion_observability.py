from pathlib import Path

from fastapi.testclient import TestClient

from app.connectors.repository import ArchiveRepositoryIngestor
from app.db.session import SessionLocal
from app.main import app
from app.models.entity import Entity

client = TestClient(app)


def test_archive_repository_ingestor_returns_observable_report(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    db = SessionLocal()

    try:
        entity = Entity(title="Observable Repository", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()

        text = "Repository observability verifies bytes and result metadata.\n"
        (repo / "README.md").write_text(text, encoding="utf-8")

        report = ArchiveRepositoryIngestor(db).ingest_repository(
            entity_id=entity.id,
            repository_path=repo,
        )

        assert report.discovered_count == 1
        assert report.document_count == 1
        assert report.processing_job_count == 1
        assert report.bytes_ingested == len(text.encode("utf-8"))
        assert report.elapsed_ms >= 0
        assert report.skipped_count == 0
        assert report.unsupported_count == 0
        assert report.failures == []

    finally:
        db.close()


def test_repository_ingestion_api_returns_observable_report(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity_response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "repository",
            "title": "Observable Repository API",
        },
    )
    assert entity_response.status_code == 201
    entity = entity_response.json()

    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    text = "Repository API observability returns expanded metadata.\n"
    (repo / "README.md").write_text(text, encoding="utf-8")

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
    assert data["bytes_ingested"] == len(text.encode("utf-8"))
    assert data["elapsed_ms"] >= 0
    assert data["skipped_count"] == 0
    assert data["unsupported_count"] == 0
    assert data["failures"] == []
