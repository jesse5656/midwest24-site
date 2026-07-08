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


def test_repository_ingested_markdown_is_processed_into_searchable_artifacts(
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

    text = (
        "# Midwest24 Repository Knowledge\n\n"
        "Repository ingestion should make local knowledge discoverable.\n\n"
        "The Archive semantic search API should return repository markdown chunks.\n"
    )

    (repo / "README.md").write_text(text, encoding="utf-8")

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

        document = (
            db.execute(
                select(Document).where(Document.entity_id == entity["id"])
            ).scalar_one()
        )

        document_text = (
            db.execute(
                select(DocumentText).where(DocumentText.document_id == document.id)
            ).scalar_one()
        )

        chunks = list(
            db.execute(
                select(DocumentChunk).where(
                    DocumentChunk.document_text_id == document_text.id
                )
            ).scalars()
        )

        embeddings = list(
            db.execute(
                select(DocumentEmbedding).where(
                    DocumentEmbedding.document_chunk_id.in_([chunk.id for chunk in chunks])
                )
            ).scalars()
        )

        assert "Repository ingestion should make local knowledge discoverable." in document_text.text
        assert len(chunks) >= 1
        assert len(embeddings) == len(chunks)

    finally:
        db.close()
