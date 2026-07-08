from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.processing_job import ProcessingJob


@dataclass(frozen=True)
class ProcessingJobStatusCounts:
    pending: int = 0
    running: int = 0
    completed: int = 0
    failed: int = 0
    total: int = 0


class RepositoryProcessingJobStatistics:
    def __init__(self, db: Session):
        self.db = db

    def count_for_documents(self, document_ids: list[UUID]) -> ProcessingJobStatusCounts:
        if not document_ids:
            return ProcessingJobStatusCounts()

        jobs = list(
            self.db.execute(
                select(ProcessingJob).where(ProcessingJob.document_id.in_(document_ids))
            ).scalars()
        )

        return ProcessingJobStatusCounts(
            pending=sum(1 for job in jobs if job.status == "pending"),
            running=sum(1 for job in jobs if job.status == "running"),
            completed=sum(1 for job in jobs if job.status == "completed"),
            failed=sum(1 for job in jobs if job.status == "failed"),
            total=len(jobs),
        )
