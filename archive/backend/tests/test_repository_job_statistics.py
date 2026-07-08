from uuid import uuid4

from app.connectors.repository import RepositoryProcessingJobStatistics
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.entity import Entity
from app.models.processing_job import ProcessingJob


def test_repository_processing_job_statistics_counts_statuses():
    db = SessionLocal()

    try:
        entity = Entity(title="Job Statistics Entity", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        document = Document(
            entity_id=entity.id,
            filename="README.md",
            mime_type="text/markdown",
            storage_path="/tmp/README.md",
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        for status in ["pending", "running", "completed", "failed"]:
            db.add(
                ProcessingJob(
                    document_id=document.id,
                    job_type="repository_document_ingestion",
                    status=status,
                )
            )

        db.commit()

        counts = RepositoryProcessingJobStatistics(db).count_for_documents([document.id])

        assert counts.pending == 1
        assert counts.running == 1
        assert counts.completed == 1
        assert counts.failed == 1
        assert counts.total == 4

    finally:
        db.close()


def test_repository_processing_job_statistics_returns_zero_counts_for_empty_document_list():
    db = SessionLocal()

    try:
        counts = RepositoryProcessingJobStatistics(db).count_for_documents([])

        assert counts.pending == 0
        assert counts.running == 0
        assert counts.completed == 0
        assert counts.failed == 0
        assert counts.total == 0

    finally:
        db.close()


def test_repository_processing_job_statistics_ignores_other_documents():
    db = SessionLocal()

    try:
        first_entity = Entity(title="First", entity_type="repository")
        second_entity = Entity(title="Second", entity_type="repository")
        db.add(first_entity)
        db.add(second_entity)
        db.commit()
        db.refresh(first_entity)
        db.refresh(second_entity)

        first_document = Document(
            entity_id=first_entity.id,
            filename="FIRST.md",
            mime_type="text/markdown",
            storage_path="/tmp/FIRST.md",
        )
        second_document = Document(
            entity_id=second_entity.id,
            filename="SECOND.md",
            mime_type="text/markdown",
            storage_path="/tmp/SECOND.md",
        )
        db.add(first_document)
        db.add(second_document)
        db.commit()
        db.refresh(first_document)
        db.refresh(second_document)

        db.add(
            ProcessingJob(
                document_id=first_document.id,
                job_type="repository_document_ingestion",
                status="pending",
            )
        )
        db.add(
            ProcessingJob(
                document_id=second_document.id,
                job_type="repository_document_ingestion",
                status="completed",
            )
        )
        db.commit()

        counts = RepositoryProcessingJobStatistics(db).count_for_documents([first_document.id])

        assert counts.pending == 1
        assert counts.completed == 0
        assert counts.total == 1

    finally:
        db.close()
