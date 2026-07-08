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


def test_repository_incremental_ingestion_api_ingests_new_files(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Incremental API New")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# New API\n", encoding="utf-8")

    response = client.post(
        "/api/v1/repository-incremental-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
            "manifest_path": str(tmp_path / "manifest.json"),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["new_count"] == 1
    assert data["modified_count"] == 0
    assert data["deleted_count"] == 0
    assert data["changed_count"] == 1
    assert data["ingested_document_count"] == 1
    assert data["processing_job_count"] == 1
    assert data["manifest_updated"] is True
    assert data["ingestion_report"]["document_count"] == 1
    assert data["ingestion_report"]["processing_jobs_by_status"]["pending"] == 1


def test_repository_incremental_ingestion_api_reports_no_changes_on_second_run(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Incremental API Stable")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Stable API\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"

    payload = {
        "entity_id": entity["id"],
        "repository_path": str(repo),
        "manifest_path": str(manifest_path),
    }

    first = client.post("/api/v1/repository-incremental-ingestions", json=payload)
    second = client.post("/api/v1/repository-incremental-ingestions", json=payload)

    assert first.status_code == 201
    assert second.status_code == 201

    data = second.json()

    assert data["changed_count"] == 0
    assert data["ingestion_report"] is None
    assert data["ingested_document_count"] == 0
    assert data["processing_job_count"] == 0


def test_repository_incremental_ingestion_api_reports_modified_files(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Incremental API Modified")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# One\n", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"

    payload = {
        "entity_id": entity["id"],
        "repository_path": str(repo),
        "manifest_path": str(manifest_path),
    }

    first = client.post("/api/v1/repository-incremental-ingestions", json=payload)
    assert first.status_code == 201

    (repo / "README.md").write_text("# Two\n", encoding="utf-8")

    response = client.post("/api/v1/repository-incremental-ingestions", json=payload)

    data = response.json()

    assert response.status_code == 201
    assert data["modified_count"] == 1
    assert data["changes"]["modified_files"] == ["README.md"]


def test_repository_incremental_ingestion_api_rejects_unknown_entity(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Unknown Entity\n", encoding="utf-8")

    response = client.post(
        "/api/v1/repository-incremental-ingestions",
        json={
            "entity_id": "00000000-0000-0000-0000-000000000000",
            "repository_path": str(repo),
            "manifest_path": str(tmp_path / "manifest.json"),
        },
    )

    assert response.status_code == 404


def test_repository_incremental_ingestion_api_rejects_missing_repository_path(tmp_path: Path):
    entity = create_entity("Incremental API Missing Path")

    response = client.post(
        "/api/v1/repository-incremental-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(tmp_path / "missing"),
            "manifest_path": str(tmp_path / "manifest.json"),
        },
    )

    assert response.status_code == 400
