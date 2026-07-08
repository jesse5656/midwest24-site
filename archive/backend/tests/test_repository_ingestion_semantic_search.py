from pathlib import Path

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.workers.document_worker import DocumentWorker

client = TestClient(app)


def test_repository_ingested_markdown_is_discoverable_by_semantic_search(
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
            "title": "Repository Semantic Search Test",
        },
    ).json()

    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    (repo / "README.md").write_text(
        "# Midwest24 Repository Knowledge\n\n"
        "Repository ingestion should make local knowledge discoverable.\n\n"
        "The Archive semantic search API should return repository markdown chunks.\n",
        encoding="utf-8",
    )

    ingestion = client.post(
        "/api/v1/repository-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
        },
    )

    assert ingestion.status_code == 201
    assert ingestion.json()["document_count"] == 1

    db = SessionLocal()

    try:
        repository_job = (
            db.query(ProcessingJob)
            .join(Document, ProcessingJob.document_id == Document.id)
            .filter(ProcessingJob.status == "pending")
            .filter(Document.entity_id == entity["id"])
            .one()
        )

        worker = DocumentWorker(db)
        worker.process(repository_job)

    finally:
        db.close()

    response = client.post(
        "/api/v1/search/semantic",
        json={
            "query": "repository markdown knowledge",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    results = response.json()

    matching_results = [
        result for result in results
        if result["entity_id"] == entity["id"]
    ]

    assert len(matching_results) >= 1

    first = matching_results[0]

    assert first["entity_title"] == "Repository Semantic Search Test"
    assert first["filename"] == "README.md"
    assert "repository" in first["text"].lower()
    assert "chunk_id" in first
    assert "document_id" in first
    assert isinstance(first["distance"], float)
