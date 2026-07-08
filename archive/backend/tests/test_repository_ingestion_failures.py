from pathlib import Path

from sqlalchemy import select

from app.connectors.repository import ArchiveRepositoryIngestor
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.entity import Entity
from app.models.processing_job import ProcessingJob


class FailingFileCopier:
    def copy(self, source_path, destination_path):
        raise RuntimeError(f"copy failed for {Path(source_path).name}")


class SelectiveFailingFileCopier:
    def copy(self, source_path, destination_path):
        if Path(source_path).name == "FAIL.md":
            raise RuntimeError("selective copy failure")
        destination_path.write_text(
            Path(source_path).read_text(encoding="utf-8"),
            encoding="utf-8",
        )


def test_archive_repository_ingestor_reports_copy_failures_without_documents_or_jobs(
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
        entity = Entity(title="Failure Repository", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()
        (repo / "README.md").write_text("# Failure\n", encoding="utf-8")

        report = ArchiveRepositoryIngestor(
            db,
            file_copier=FailingFileCopier(),
        ).ingest_repository(entity.id, repo)

        assert report.discovered_count == 1
        assert report.document_count == 0
        assert report.processing_job_count == 0
        assert len(report.failures) == 1
        assert report.failures[0].path == "README.md"
        assert "copy failed" in report.failures[0].reason

        documents = list(
            db.execute(
                select(Document).where(Document.entity_id == entity.id)
            ).scalars()
        )

        jobs_for_entity = list(
            db.execute(
                select(ProcessingJob)
                .join(Document, ProcessingJob.document_id == Document.id)
                .where(Document.entity_id == entity.id)
            ).scalars()
        )

        assert documents == []
        assert jobs_for_entity == []

    finally:
        db.close()


def test_archive_repository_ingestor_continues_after_one_file_copy_failure(
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
        entity = Entity(title="Partial Failure Repository", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()
        (repo / "FAIL.md").write_text("# Fail\n", encoding="utf-8")
        (repo / "README.md").write_text("# Success\n", encoding="utf-8")

        report = ArchiveRepositoryIngestor(
            db,
            file_copier=SelectiveFailingFileCopier(),
        ).ingest_repository(entity.id, repo)

        assert report.discovered_count == 2
        assert report.document_count == 1
        assert report.processing_job_count == 1
        assert len(report.failures) == 1
        assert report.failures[0].path == "FAIL.md"
        assert report.bytes_ingested == len("# Success\n".encode("utf-8"))

        documents = list(
            db.execute(
                select(Document).where(Document.entity_id == entity.id)
            ).scalars()
        )

        assert len(documents) == 1
        assert documents[0].filename == "README.md"

    finally:
        db.close()


def test_archive_repository_ingestor_rolls_back_failed_file_before_next_file(
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
        entity = Entity(title="Rollback Failure Repository", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()
        (repo / "FAIL.md").write_text("# Fail\n", encoding="utf-8")
        (repo / "OK.md").write_text("# OK\n", encoding="utf-8")

        report = ArchiveRepositoryIngestor(
            db,
            file_copier=SelectiveFailingFileCopier(),
        ).ingest_repository(entity.id, repo)

        assert report.document_count == 1
        assert report.processing_job_count == 1
        assert len(report.failures) == 1

        documents = list(
            db.execute(
                select(Document)
                .where(Document.entity_id == entity.id)
                .order_by(Document.filename.asc())
            ).scalars()
        )

        assert [document.filename for document in documents] == ["OK.md"]

    finally:
        db.close()


def test_archive_repository_ingestor_reports_failure_without_counting_failed_bytes(
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
        entity = Entity(title="Failure Bytes Repository", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()
        (repo / "README.md").write_text("# Fail Bytes\n", encoding="utf-8")

        report = ArchiveRepositoryIngestor(
            db,
            file_copier=FailingFileCopier(),
        ).ingest_repository(entity.id, repo)

        assert report.bytes_ingested == 0
        assert report.document_count == 0
        assert len(report.failures) == 1

    finally:
        db.close()


def test_repository_ingestion_failure_report_shape_preserves_path_and_reason(
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
        entity = Entity(title="Failure Shape Repository", entity_type="repository")
        db.add(entity)
        db.commit()
        db.refresh(entity)

        repo = tmp_path / "knowledge-repo"
        repo.mkdir()
        (repo / "README.md").write_text("# Failure Shape\n", encoding="utf-8")

        report = ArchiveRepositoryIngestor(
            db,
            file_copier=FailingFileCopier(),
        ).ingest_repository(entity.id, repo)

        failure = report.failures[0]

        assert failure.path == "README.md"
        assert "copy failed for README.md" in failure.reason

    finally:
        db.close()
