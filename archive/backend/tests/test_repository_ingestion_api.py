from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models.document import Document
from app.models.processing_job import ProcessingJob

client = TestClient(app)


def test_create_repository_ingestion_api_creates_documents_and_processing_jobs(
    tmp_path: Path,
    monkeypatch,
):
    storage_root = tmp_path / "archive-storage"
    monkeypatch.setattr(
        "app.connectors.repository.archive_repository_ingestor.settings.document_storage_root",
        str(storage_root),
    )

    entity_response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "repository",
            "title": "Repository API Test Entity",
        },
    )
    assert entity_response.status_code == 201
    entity = entity_response.json()

    repo = tmp_path / "knowledge-repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")
    (repo / "OPERATING-PLAN.md").write_text("Execute the Operating Plan.\n", encoding="utf-8")
    (repo / "image.png").write_bytes(b"skip")

    response = client.post(
        "/api/v1/repository-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["discovered_count"] == 2
    assert data["document_count"] == 2
    assert data["processing_job_count"] == 2

    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        documents = list(
            db.execute(
                select(Document)
                .where(Document.entity_id == entity["id"])
                .order_by(Document.filename.asc())
            ).scalars()
        )

        assert [document.filename for document in documents] == [
            "OPERATING-PLAN.md",
            "README.md",
        ]

        jobs = list(
            db.execute(
                select(ProcessingJob).where(
                    ProcessingJob.document_id.in_([document.id for document in documents])
                )
            ).scalars()
        )

        assert len(jobs) == 2

    finally:
        db.close()


def test_create_repository_ingestion_api_rejects_unknown_entity(tmp_path: Path):
    repo = tmp_path / "knowledge-repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")

    response = client.post(
        "/api/v1/repository-ingestions",
        json={
            "entity_id": "00000000-0000-0000-0000-000000000000",
            "repository_path": str(repo),
        },
    )

    assert response.status_code == 404
