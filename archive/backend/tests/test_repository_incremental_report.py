from app.connectors.repository import RepositoryChangeSet, RepositoryIncrementalIngestionReport, RepositoryIngestionReport


def test_incremental_report_counts_changes_without_ingestion_report():
    report = RepositoryIncrementalIngestionReport(
        changes=RepositoryChangeSet(
            new_files=["a.md"],
            modified_files=["b.md"],
            deleted_files=["c.md"],
            unchanged_files=["d.md"],
        ),
        manifest_updated=True,
        ingestion_report=None,
    )

    assert report.new_count == 1
    assert report.modified_count == 1
    assert report.deleted_count == 1
    assert report.unchanged_count == 1
    assert report.changed_count == 3
    assert report.ingested_document_count == 0
    assert report.processing_job_count == 0


def test_incremental_report_exposes_nested_ingestion_counts():
    report = RepositoryIncrementalIngestionReport(
        changes=RepositoryChangeSet(new_files=["a.md"]),
        manifest_updated=True,
        ingestion_report=RepositoryIngestionReport(document_count=2, processing_job_count=2),
    )

    assert report.ingested_document_count == 2
    assert report.processing_job_count == 2
