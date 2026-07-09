from app.connectors.repository import (
    ProcessingJobStatusCounts,
    RepositoryChangeSet,
    RepositoryDuplicateFile,
    RepositoryIncrementalIngestionReport,
    RepositoryIncrementalSummaryBuilder,
    RepositoryIngestionFailure,
    RepositoryIngestionReport,
    RepositoryIngestionSummaryBuilder,
    RepositorySkippedPath,
    RepositoryUnsupportedFile,
)


def test_ingestion_summary_reports_ingested_outcome():
    report = RepositoryIngestionReport(document_count=2, processing_job_count=2)

    summary = RepositoryIngestionSummaryBuilder().build(report)

    assert summary.outcome == "ingested"
    assert summary.action_required is False
    assert "2 document" in summary.message


def test_ingestion_summary_reports_partial_failure_outcome():
    report = RepositoryIngestionReport(
        document_count=1,
        processing_job_count=1,
        failures=[RepositoryIngestionFailure(path="bad.md", reason="copy failed")],
    )

    summary = RepositoryIngestionSummaryBuilder().build(report)

    assert summary.outcome == "partial_failure"
    assert summary.action_required is True
    assert summary.has_failures is True


def test_ingestion_summary_reports_duplicates_only_outcome():
    report = RepositoryIngestionReport(
        discovered_count=1,
        duplicate_count=1,
        duplicate_files=[RepositoryDuplicateFile(path="README.md")],
    )

    summary = RepositoryIngestionSummaryBuilder().build(report)

    assert summary.outcome == "duplicates_only"
    assert summary.has_duplicates is True
    assert summary.action_required is False


def test_ingestion_summary_reports_no_supported_files_with_unsupported_files():
    report = RepositoryIngestionReport(
        discovered_count=0,
        unsupported_count=1,
        unsupported_files=[RepositoryUnsupportedFile(path="image.png", suffix=".png")],
    )

    summary = RepositoryIngestionSummaryBuilder().build(report)

    assert summary.outcome == "nothing_ingested"
    assert summary.has_unsupported_files is True
    assert summary.action_required is False


def test_ingestion_summary_reports_skipped_paths_flag():
    report = RepositoryIngestionReport(
        discovered_count=0,
        skipped_count=1,
        skipped_paths=[RepositorySkippedPath(path=".git", reason="excluded_directory:.git")],
    )

    summary = RepositoryIngestionSummaryBuilder().build(report)

    assert summary.has_skipped_paths is True
    assert summary.outcome == "nothing_ingested"


def test_ingestion_summary_reports_mixed_observability_flags():
    report = RepositoryIngestionReport(
        document_count=1,
        processing_job_count=1,
        skipped_count=1,
        unsupported_count=1,
        duplicate_count=1,
        skipped_paths=[RepositorySkippedPath(path=".git", reason="excluded_directory:.git")],
        unsupported_files=[RepositoryUnsupportedFile(path="image.png", suffix=".png")],
        duplicate_files=[RepositoryDuplicateFile(path="README.md")],
    )

    summary = RepositoryIngestionSummaryBuilder().build(report)

    assert summary.outcome == "ingested"
    assert summary.has_duplicates is True
    assert summary.has_unsupported_files is True
    assert summary.has_skipped_paths is True


def test_incremental_summary_reports_no_changes():
    report = RepositoryIncrementalIngestionReport(
        changes=RepositoryChangeSet(),
        manifest_updated=True,
        ingestion_report=None,
    )

    summary = RepositoryIncrementalSummaryBuilder().build(report)

    assert summary.outcome == "no_changes"
    assert summary.action_required is False
    assert summary.changed_count == 0
    assert summary.ingested_document_count == 0


def test_incremental_summary_reports_changes_ingested():
    report = RepositoryIncrementalIngestionReport(
        changes=RepositoryChangeSet(new_files=["README.md"]),
        manifest_updated=True,
        ingestion_report=RepositoryIngestionReport(document_count=1, processing_job_count=1),
    )

    summary = RepositoryIncrementalSummaryBuilder().build(report)

    assert summary.outcome == "changes_ingested"
    assert summary.action_required is False
    assert summary.changed_count == 1
    assert summary.ingested_document_count == 1


def test_incremental_summary_reports_partial_failure():
    report = RepositoryIncrementalIngestionReport(
        changes=RepositoryChangeSet(new_files=["README.md"]),
        manifest_updated=True,
        ingestion_report=RepositoryIngestionReport(
            failures=[RepositoryIngestionFailure(path="README.md", reason="copy failed")]
        ),
    )

    summary = RepositoryIncrementalSummaryBuilder().build(report)

    assert summary.outcome == "partial_failure"
    assert summary.action_required is True
    assert summary.changed_count == 1


def test_incremental_summary_counts_modified_and_deleted_changes():
    report = RepositoryIncrementalIngestionReport(
        changes=RepositoryChangeSet(
            modified_files=["A.md"],
            deleted_files=["B.md"],
        ),
        manifest_updated=True,
        ingestion_report=None,
    )

    summary = RepositoryIncrementalSummaryBuilder().build(report)

    assert summary.changed_count == 2
