from io import BytesIO

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.processing_job import ProcessingJob
from app.workers.document_worker import DocumentWorker

client = TestClient(app)


def test_semantic_search_returns_processed_chunks():
    entity = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "Semantic Pipeline Test",
        },
    ).json()

    document = client.post(
        f"/api/v1/entities/{entity['id']}/documents",
        files={
            "file": (
                "semantic-pipeline.txt",
                BytesIO(b"Roof storm inspection and insurance supplement workflow."),
                "text/plain",
            )
        },
    ).json()

    job = client.post(
        "/api/v1/processing-jobs",
        json={
            "document_id": document["id"],
            "job_type": "extract_text",
        },
    ).json()

    db = SessionLocal()
    worker = DocumentWorker(db)
    worker.process(db.get(ProcessingJob, job["id"]))
    db.close()

    response = client.post(
        "/api/v1/search/semantic",
        json={
            "query": "storm inspection",
            "limit": 5,
        },
    )

    assert response.status_code == 200

    results = response.json()
    assert isinstance(results, list)
    assert len(results) >= 1

    first = results[0]
    assert "chunk_id" in first
    assert "text" in first
    assert "distance" in first
    assert isinstance(first["text"], str)
    assert isinstance(first["distance"], float)
