from app.connectors.repository import RepositoryDuplicateDetector
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.entity import Entity


class FakeRepositoryFile:
    def __init__(self, relative_path: str):
        self.relative_path = relative_path


def test_duplicate_detector_reports_existing_document_for_entity():
    db = SessionLocal()

    try:
        entity = Entity(title="Duplicate Detector Entity", entity_type="repository")
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

        detector = RepositoryDuplicateDetector(db)

        assert detector.exists_for_entity(entity.id, "README.md") is True

    finally:
        db.close()


def test_duplicate_detector_does_not_report_missing_document():
    db = SessionLocal()

    try:
        entity = Entity(title="Missing Duplicate Entity", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        detector = RepositoryDuplicateDetector(db)

        assert detector.exists_for_entity(entity.id, "README.md") is False

    finally:
        db.close()


def test_duplicate_detector_filters_new_and_duplicate_files():
    db = SessionLocal()

    try:
        entity = Entity(title="Filter Duplicate Entity", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        db.add(
            Document(
                entity_id=entity.id,
                filename="README.md",
                mime_type="text/markdown",
                storage_path="/tmp/README.md",
            )
        )
        db.commit()

        detector = RepositoryDuplicateDetector(db)

        new_files, duplicates = detector.filter_new_files(
            entity.id,
            [
                FakeRepositoryFile("README.md"),
                FakeRepositoryFile("OPERATING-PLAN.md"),
            ],
        )

        assert [item.relative_path for item in new_files] == ["OPERATING-PLAN.md"]
        assert [item.path for item in duplicates] == ["README.md"]
        assert duplicates[0].reason == "document_already_exists_for_entity"

    finally:
        db.close()


def test_duplicate_detector_is_entity_scoped():
    db = SessionLocal()

    try:
        first = Entity(title="First Duplicate Entity", entity_type="repository")
        second = Entity(title="Second Duplicate Entity", entity_type="repository")
        db.add(first)
        db.add(second)
        db.commit()
        db.refresh(first)
        db.refresh(second)

        db.add(
            Document(
                entity_id=first.id,
                filename="README.md",
                mime_type="text/markdown",
                storage_path="/tmp/README.md",
            )
        )
        db.commit()

        detector = RepositoryDuplicateDetector(db)

        assert detector.exists_for_entity(first.id, "README.md") is True
        assert detector.exists_for_entity(second.id, "README.md") is False

    finally:
        db.close()
