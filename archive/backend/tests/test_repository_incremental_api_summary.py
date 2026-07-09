from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_entity(title: str):
    response = client.post(
        "/api/v1/entities",
        json={"entity_type": "repository", "title": title},
    )
    assert response.status_code == 201
    return response.json()


def test_incremental_api_returns_changes_ingested_summary(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Incremental Summary Repository")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Incremental Summary\n", encoding="utf-8")

    response = client.post(
        "/api/v1/repository-incremental-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
            "manifest_path": str(tmp_path / "manifest.json"),
        },
    )

    assert response.status_code == 201
    assert response.json()["summary"]["outcome"] == "changes_ingested"
    assert response.json()["summary"]["changed_count"] == 1


def test_incremental_api_returns_no_changes_summary_on_second_run(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Incremental No Change Summary Repository")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# No Change Summary\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"

    payload = {
        "entity_id": entity["id"],
        "repository_path": str(repo),
        "manifest_path": str(manifest_path),
    }

    client.post("/api/v1/repository-incremental-ingestions", json=payload)
    response = client.post("/api/v1/repository-incremental-ingestions", json=payload)

    assert response.status_code == 201
    assert response.json()["summary"]["outcome"] == "no_changes"
    assert response.json()["summary"]["action_required"] is False


def test_incremental_api_summary_counts_modified_file(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Incremental Modified Summary Repository")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# One\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"

    payload = {
        "entity_id": entity["id"],
        "repository_path": str(repo),
        "manifest_path": str(manifest_path),
    }

    client.post("/api/v1/repository-incremental-ingestions", json=payload)

    (repo / "README.md").write_text("# Two\n", encoding="utf-8")

    response = client.post("/api/v1/repository-incremental-ingestions", json=payload)

    assert response.status_code == 201
    assert response.json()["summary"]["outcome"] == "changes_ingested"
    assert response.json()["summary"]["changed_count"] == 1


def test_incremental_api_summary_counts_deleted_file(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Incremental Deleted Summary Repository")

    repo = tmp_path / "repo"
    repo.mkdir()
    readme = repo / "README.md"
    readme.write_text("# Delete\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"

    payload = {
        "entity_id": entity["id"],
        "repository_path": str(repo),
        "manifest_path": str(manifest_path),
    }

    client.post("/api/v1/repository-incremental-ingestions", json=payload)
    readme.unlink()

    response = client.post("/api/v1/repository-incremental-ingestions", json=payload)

    assert response.status_code == 201
    assert response.json()["summary"]["changed_count"] == 1
    assert response.json()["deleted_count"] == 1


def test_incremental_api_summary_exposes_ingested_document_count(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Incremental Ingested Count Summary Repository")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Count\n", encoding="utf-8")

    response = client.post(
        "/api/v1/repository-incremental-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
            "manifest_path": str(tmp_path / "manifest.json"),
        },
    )

    assert response.status_code == 201
    assert response.json()["summary"]["ingested_document_count"] == 1
