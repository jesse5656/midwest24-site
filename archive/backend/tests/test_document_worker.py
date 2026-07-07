from io import BytesIO

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models.document_text import DocumentText
from app.models.processing_job import ProcessingJob
from app.workers.document_worker import DocumentWorker

client = TestClient(app)


def test_worker_extracts_plain_text():
    entity = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "Worker Extraction Test",
        },
    ).json()

    document = client.post(
        f"/api/v1/entities/{entity['id']}/documents",
        files={
            "file": (
                "worker-test.txt",
                BytesIO(b"Hello Midwest24 Archive"),
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

    job_model = db.get(ProcessingJob, job["id"])

    worker = DocumentWorker(db)
    worker.process(job_model)

    extracted = db.execute(
        select(DocumentText).where(
            DocumentText.document_id == document["id"]
        )
    ).scalar_one()

    assert extracted.text == "Hello Midwest24 Archive"
    assert extracted.character_count == len("Hello Midwest24 Archive")

    db.close()
