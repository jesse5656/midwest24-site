import json
from io import BytesIO

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models.document_chunk import DocumentChunk
from app.models.document_embedding import DocumentEmbedding
from app.models.document_text import DocumentText
from app.models.processing_job import ProcessingJob
from app.workers.document_worker import DocumentWorker

client = TestClient(app)


def test_worker_creates_embeddings_for_chunks():
    entity = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "Embedding Test",
        },
    ).json()

    document = client.post(
        f"/api/v1/entities/{entity['id']}/documents",
        files={
            "file": (
                "embedding-test.txt",
                BytesIO(b"Embedding paragraph one.\n\nEmbedding paragraph two."),
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

    text_row = db.execute(
        select(DocumentText).where(DocumentText.document_id == document["id"])
    ).scalar_one()

    chunk = db.execute(
        select(DocumentChunk).where(DocumentChunk.document_text_id == text_row.id)
    ).scalars().first()

    embedding = db.execute(
        select(DocumentEmbedding).where(DocumentEmbedding.document_chunk_id == chunk.id)
    ).scalar_one()

    vector = json.loads(embedding.embedding_json)

    assert embedding.embedding_model == "mock"
    assert isinstance(vector, list)
    assert len(vector) == 16

    db.close()
