from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.connectors.repository import (
    ArchiveRepositoryIngestor,
    REPOSITORY_DOCUMENT_JOB_TYPE,
)
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.entity import Entity
from app.models.processing_job import ProcessingJob


def test_archive_repository_ingestor_creates_documents_and_processing_jobs(
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
        entity = create_entity(db)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()
        (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")
        (repo / "OPERATING-PLAN.md").write_text(
            "Execute the Operating Plan.\n",
            encoding="utf-8",
        )
        (repo / "image.png").write_bytes(b"skip")

        result = ArchiveRepositoryIngestor(db).ingest_repository(
            entity_id=entity.id,
            repository_path=repo,
        )

        assert result.discovered_count == 2
        assert result.document_count == 2
        assert result.processing_job_count == 2

        documents = list(
            db.execute(
                select(Document)
                .where(Document.entity_id == entity.id)
                .order_by(Document.filename.asc())
            ).scalars()
        )

        assert [document.filename for document in documents] == [
            "OPERATING-PLAN.md",
            "README.md",
        ]

        for document in documents:
            stored_path = Path(document.storage_path)
            assert stored_path.exists()
            assert stored_path.parent == storage_root

        jobs = list(
            db.execute(
                select(ProcessingJob).where(
                    ProcessingJob.document_id.in_([document.id for document in documents])
                )
            ).scalars()
        )

        assert len(jobs) == 2
        assert {job.document_id for job in jobs} == {document.id for document in documents}
        assert {job.job_type for job in jobs} == {REPOSITORY_DOCUMENT_JOB_TYPE}

    finally:
        db.close()


def test_archive_repository_ingestor_rejects_unknown_entity(tmp_path: Path):
    repo = tmp_path / "knowledge-repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")

    db = SessionLocal()

    try:
        with pytest.raises(HTTPException) as exc:
            ArchiveRepositoryIngestor(db).ingest_repository(
                entity_id="00000000-0000-0000-0000-000000000000",
                repository_path=repo,
            )

        assert exc.value.status_code == 404

    finally:
        db.close()


def create_entity(db):
    entity = Entity(
        title="Knowledge Repository",
        entity_type="repository",
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity
