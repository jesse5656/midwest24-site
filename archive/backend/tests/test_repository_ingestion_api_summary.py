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


def test_repository_ingestion_api_returns_ingested_summary(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Summary Repository")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Summary\n", encoding="utf-8")

    response = client.post(
        "/api/v1/repository-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
        },
    )

    assert response.status_code == 201
    assert response.json()["summary"]["outcome"] == "ingested"
    assert response.json()["summary"]["action_required"] is False


def test_repository_ingestion_api_returns_duplicate_summary_on_second_run(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Summary Duplicate Repository")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Duplicate Summary\n", encoding="utf-8")

    payload = {
        "entity_id": entity["id"],
        "repository_path": str(repo),
    }

    first = client.post("/api/v1/repository-ingestions", json=payload)
    second = client.post("/api/v1/repository-ingestions", json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json()["summary"]["outcome"] == "duplicates_only"
    assert second.json()["summary"]["has_duplicates"] is True


def test_repository_ingestion_api_summary_reports_unsupported_files(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Summary Unsupported Repository")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "image.png").write_bytes(b"skip")

    response = client.post(
        "/api/v1/repository-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
        },
    )

    assert response.status_code == 201
    assert response.json()["summary"]["outcome"] == "nothing_ingested"
    assert response.json()["summary"]["has_unsupported_files"] is True


def test_repository_ingestion_api_summary_reports_skipped_paths(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Summary Skipped Repository")

    repo = tmp_path / "repo"
    repo.mkdir()
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
    assert response.json()["summary"]["outcome"] == "nothing_ingested"
    assert response.json()["summary"]["has_skipped_paths"] is True


def test_repository_ingestion_api_summary_in_nested_incremental_report(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = create_entity("Nested Summary Repository")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Nested Summary\n", encoding="utf-8")

    response = client.post(
        "/api/v1/repository-incremental-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
            "manifest_path": str(tmp_path / "manifest.json"),
        },
    )

    assert response.status_code == 201
    assert response.json()["ingestion_report"]["summary"]["outcome"] == "ingested"
