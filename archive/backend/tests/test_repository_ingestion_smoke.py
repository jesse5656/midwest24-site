from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_embedding import DocumentEmbedding
from app.models.document_text import DocumentText
from app.models.processing_job import ProcessingJob
from app.workers.document_worker import DocumentWorker

client = TestClient(app)


def test_repository_ingestion_smoke_processes_markdown_into_text_chunks_and_embeddings(
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
            "title": "Repository Smoke Test Entity",
        },
    )
    assert entity_response.status_code == 201
    entity = entity_response.json()

    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    markdown_text = (
        "# Repository Smoke Test\n\n"
        "Midwest24 Archive should ingest repository markdown files.\n\n"
        "The worker should extract text, create chunks, and store embeddings.\n"
    )

    (repo / "README.md").write_text(markdown_text, encoding="utf-8")

    ingestion_response = client.post(
        "/api/v1/repository-ingestions",
        json={
            "entity_id": entity["id"],
            "repository_path": str(repo),
        },
    )

    assert ingestion_response.status_code == 201
    assert ingestion_response.json()["document_count"] == 1
    assert ingestion_response.json()["processing_job_count"] == 1

    db = SessionLocal()

    try:
        document = db.execute(
            select(Document).where(Document.entity_id == entity["id"])
        ).scalar_one()

        job = db.execute(
            select(ProcessingJob).where(ProcessingJob.document_id == document.id)
        ).scalar_one()

        worker = DocumentWorker(db)
        worker.process(job)

        text_row = db.execute(
            select(DocumentText).where(DocumentText.document_id == document.id)
        ).scalar_one()

        assert "Midwest24 Archive should ingest repository markdown files." in text_row.text

        chunks = list(
            db.execute(
                select(DocumentChunk).where(DocumentChunk.document_text_id == text_row.id)
            ).scalars()
        )

        assert len(chunks) >= 1

        embeddings = list(
            db.execute(
                select(DocumentEmbedding).where(
                    DocumentEmbedding.document_chunk_id.in_([chunk.id for chunk in chunks])
                )
            ).scalars()
        )

        assert len(embeddings) == len(chunks)

        refreshed_job = db.get(ProcessingJob, job.id)
        assert refreshed_job.status == "completed"
        assert refreshed_job.progress == 100

    finally:
        db.close()
