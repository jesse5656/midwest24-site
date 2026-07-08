from pathlib import Path
from uuid import uuid4

from app.db.session import SessionLocal
from app.models.document import Document
from app.models.entity import Entity
from app.models.processing_job import ProcessingJob
from app.workers.document_worker import DocumentWorker
from app.core.config import settings


def main():
    db = SessionLocal()

    storage_dir = Path(settings.document_storage_root)
    storage_dir.mkdir(parents=True, exist_ok=True)

    test_file = storage_dir / f"{uuid4()}-smoke-test.txt"
    test_file.write_text("Smoke test paragraph one.\n\nSmoke test paragraph two.")

    entity = Entity(
        entity_type="document",
        title="Smoke Pipeline Test",
        description="End-to-end pipeline smoke test",
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)

    document = Document(
        entity_id=entity.id,
        filename=test_file.name,
        mime_type="text/plain",
        storage_path=str(test_file),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    job = ProcessingJob(
        document_id=document.id,
        job_type="extract_text",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    worker = DocumentWorker(db)
    worker.process(job)

    print("Smoke pipeline complete.")
    print(f"Entity: {entity.id}")
    print(f"Document: {document.id}")
    print(f"Job: {job.id}")
    print(f"Status: {job.status}")

    db.close()


if __name__ == "__main__":
    main()
