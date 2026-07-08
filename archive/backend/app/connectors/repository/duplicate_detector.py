from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


@dataclass(frozen=True)
class RepositoryDuplicateFile:
    path: str
    reason: str = "document_already_exists_for_entity"


class RepositoryDuplicateDetector:
    def __init__(self, db: Session):
        self.db = db

    def exists_for_entity(self, entity_id: UUID, relative_path: str) -> bool:
        return (
            self.db.execute(
                select(Document).where(
                    Document.entity_id == entity_id,
                    Document.filename == relative_path,
                )
            ).scalar_one_or_none()
            is not None
        )

    def filter_new_files(self, entity_id: UUID, repository_files: list) -> tuple[list, list[RepositoryDuplicateFile]]:
        new_files = []
        duplicates = []

        for repository_file in repository_files:
            if self.exists_for_entity(entity_id, repository_file.relative_path):
                duplicates.append(RepositoryDuplicateFile(path=repository_file.relative_path))
            else:
                new_files.append(repository_file)

        return new_files, duplicates
