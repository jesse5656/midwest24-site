from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.connectors.repository import ArchiveRepositoryIngestor
from app.db.session import SessionLocal
from app.main import app
from app.models.document import Document
from app.models.entity import Entity
from app.models.processing_job import ProcessingJob

client = TestClient(app)


def test_archive_repository_ingestor_reports_duplicates_without_creating_new_documents(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    db = SessionLocal()

    try:
        entity = Entity(title="Duplicate Repository", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()
        (repo / "README.md").write_text("# Duplicate Repo\n", encoding="utf-8")

        first_report = ArchiveRepositoryIngestor(db).ingest_repository(entity.id, repo)
        second_report = ArchiveRepositoryIngestor(db).ingest_repository(entity.id, repo)

        assert first_report.document_count == 1
        assert first_report.processing_job_count == 1
        assert first_report.duplicate_count == 0
        assert first_report.duplicate_files == []

        assert second_report.discovered_count == 1
        assert second_report.document_count == 0
        assert second_report.processing_job_count == 0
        assert second_report.duplicate_count == 1
        assert second_report.duplicate_files[0].path == "README.md"

        documents = list(
            db.execute(
                select(Document).where(Document.entity_id == entity.id)
            ).scalars()
        )
        jobs = list(db.execute(select(ProcessingJob)).scalars())

        assert len(documents) == 1
        assert len([job for job in jobs if job.document_id == documents[0].id]) == 1

    finally:
        db.close()


def test_archive_repository_ingestor_allows_same_filename_for_different_entities(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    db = SessionLocal()

    try:
        first = Entity(title="First Repository", entity_type="repository")
        second = Entity(title="Second Repository", entity_type="repository")
        db.add(first)
        db.add(second)
        db.commit()
        db.refresh(first)
        db.refresh(second)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()
        (repo / "README.md").write_text("# Shared File Name\n", encoding="utf-8")

        first_report = ArchiveRepositoryIngestor(db).ingest_repository(first.id, repo)
        second_report = ArchiveRepositoryIngestor(db).ingest_repository(second.id, repo)

        assert first_report.document_count == 1
        assert second_report.document_count == 1
        assert first_report.duplicate_count == 0
        assert second_report.duplicate_count == 0

    finally:
        db.close()


def test_repository_ingestion_api_reports_duplicate_files(tmp_path: Path, monkeypatch):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity_response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "repository",
            "title": "Duplicate Repository API",
        },
    )
    assert entity_response.status_code == 201
    entity = entity_response.json()

    repo = tmp_path / "knowledge-repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Duplicate API Repo\n", encoding="utf-8")

    first_response = client.post(
        "/api/v1/repository-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
        },
    )
    second_response = client.post(
        "/api/v1/repository-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first = first_response.json()
    second = second_response.json()

    assert first["document_count"] == 1
    assert first["duplicate_count"] == 0
    assert first["duplicate_files"] == []

    assert second["document_count"] == 0
    assert second["processing_job_count"] == 0
    assert second["duplicate_count"] == 1
    assert second["duplicate_files"][0]["path"] == "README.md"
    assert second["duplicate_files"][0]["reason"] == "document_already_exists_for_entity"


def test_repository_ingestion_api_duplicate_response_keeps_job_status_counts_zero_for_second_run(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "repository",
            "title": "Duplicate Job Counts API",
        },
    ).json()

    repo = tmp_path / "knowledge-repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Duplicate API Job Counts\n", encoding="utf-8")

    client.post(
        "/api/v1/repository-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
        },
    )

    response = client.post(
        "/api/v1/repository-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
        },
    )

    data = response.json()

    assert data["document_count"] == 0
    assert data["processing_job_count"] == 0
    assert data["processing_jobs_by_status"]["total"] == 0
