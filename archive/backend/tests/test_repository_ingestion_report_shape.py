from app.connectors.repository import (
    ProcessingJobStatusCounts,
    RepositoryDuplicateFile,
    RepositoryIngestionFailure,
    RepositoryIngestionReport,
    RepositorySkippedPath,
    RepositoryUnsupportedFile,
)


def test_repository_ingestion_report_defaults_are_operator_safe():
    report = RepositoryIngestionReport()

    assert report.discovered_count == 0
    assert report.document_count == 0
    assert report.processing_job_count == 0
    assert report.bytes_ingested == 0
    assert report.elapsed_ms == 0
    assert report.skipped_count == 0
    assert report.unsupported_count == 0
    assert report.duplicate_count == 0
    assert report.failures == []
    assert report.skipped_paths == []
    assert report.unsupported_files == []
    assert report.duplicate_files == []
    assert report.processing_jobs_by_status.total == 0


def test_repository_ingestion_report_accepts_all_observability_lists():
    report = RepositoryIngestionReport(
        failures=[RepositoryIngestionFailure(path="bad.md", reason="copy_failed")],
        skipped_paths=[RepositorySkippedPath(path=".git", reason="excluded_directory:.git")],
        unsupported_files=[RepositoryUnsupportedFile(path="image.png", suffix=".png")],
        duplicate_files=[RepositoryDuplicateFile(path="README.md")],
        processing_jobs_by_status=ProcessingJobStatusCounts(pending=1, total=1),
    )

    assert report.failures[0].path == "bad.md"
    assert report.skipped_paths[0].path == ".git"
    assert report.unsupported_files[0].suffix == ".png"
    assert report.duplicate_files[0].reason == "document_already_exists_for_entity"
    assert report.processing_jobs_by_status.pending == 1
    assert report.processing_jobs_by_status.total == 1
