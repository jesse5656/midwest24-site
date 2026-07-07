from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.processing_job import ProcessingJob
from app.workers.document_worker import DocumentWorker


def main():
    db = SessionLocal()

    job = db.execute(
        select(ProcessingJob)
        .where(ProcessingJob.status == "pending")
        .order_by(ProcessingJob.created_at.asc())
    ).scalars().first()

    if job is None:
        print("No pending jobs.")
        return

    print(f"Processing {job.id}")

    worker = DocumentWorker(db)
    worker.process(job)

    print("Done.")


if __name__ == "__main__":
    main()
