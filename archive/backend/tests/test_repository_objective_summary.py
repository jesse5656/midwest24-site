from app.connectors.repository import (
    RepositoryChangeSet,
    RepositoryDuplicateFile,
    RepositoryIncrementalIngestionReport,
    RepositoryIngestionFailure,
    RepositoryIngestionReport,
    RepositoryObjectiveSummaryBuilder,
)


def test_objective_summary_totals_single_ingestion_report():
    report = RepositoryIngestionReport(
        document_count=2,
        processing_job_count=2,
        duplicate_count=1,
        unsupported_count=3,
        skipped_count=4,
    )

    summary = RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
        "Repository Ingestion Observability",
        [report],
    )

    assert summary.objective_name == "Repository Ingestion Observability"
    assert summary.status == "complete"
    assert summary.total_documents == 2
    assert summary.total_processing_jobs == 2
    assert summary.total_duplicates == 1
    assert summary.total_unsupported == 3
    assert summary.total_skipped == 4
    assert summary.action_required is False
    assert summary.is_complete is True


def test_objective_summary_marks_attention_required_when_failures_exist():
    report = RepositoryIngestionReport(
        failures=[RepositoryIngestionFailure(path="bad.md", reason="copy failed")]
    )

    summary = RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
        "Repository Ingestion Observability",
        [report],
    )

    assert summary.status == "attention_required"
    assert summary.total_failures == 1
    assert summary.action_required is True
    assert summary.is_complete is False


def test_objective_summary_aggregates_multiple_ingestion_reports():
    first = RepositoryIngestionReport(document_count=1, processing_job_count=1)
    second = RepositoryIngestionReport(
        document_count=2,
        processing_job_count=2,
        duplicate_count=1,
        unsupported_count=1,
        skipped_count=1,
    )

    summary = RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
        "Repository Ingestion Observability",
        [first, second],
    )

    assert summary.total_documents == 3
    assert summary.total_processing_jobs == 3
    assert summary.total_duplicates == 1
    assert summary.total_unsupported == 1
    assert summary.total_skipped == 1


def test_objective_summary_handles_empty_report_list():
    summary = RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
        "Empty Objective",
        [],
    )

    assert summary.total_documents == 0
    assert summary.total_processing_jobs == 0
    assert summary.total_failures == 0
    assert summary.status == "complete"
    assert summary.is_complete is True


def test_objective_summary_aggregates_incremental_reports():
    first = RepositoryIncrementalIngestionReport(
        changes=RepositoryChangeSet(new_files=["README.md"]),
        manifest_updated=True,
        ingestion_report=RepositoryIngestionReport(document_count=1, processing_job_count=1),
    )
    second = RepositoryIncrementalIngestionReport(
        changes=RepositoryChangeSet(new_files=["PLAN.md"]),
        manifest_updated=True,
        ingestion_report=RepositoryIngestionReport(document_count=1, processing_job_count=1),
    )

    summary = RepositoryObjectiveSummaryBuilder().build_from_incremental_reports(
        "Incremental Objective",
        [first, second],
    )

    assert summary.total_documents == 2
    assert summary.total_processing_jobs == 2
    assert summary.is_complete is True


def test_objective_summary_ignores_incremental_reports_without_ingestion_report():
    report = RepositoryIncrementalIngestionReport(
        changes=RepositoryChangeSet(),
        manifest_updated=True,
        ingestion_report=None,
    )

    summary = RepositoryObjectiveSummaryBuilder().build_from_incremental_reports(
        "No Change Objective",
        [report],
    )

    assert summary.total_documents == 0
    assert summary.total_processing_jobs == 0
    assert summary.is_complete is True


def test_objective_summary_counts_incremental_failures():
    report = RepositoryIncrementalIngestionReport(
        changes=RepositoryChangeSet(new_files=["README.md"]),
        manifest_updated=True,
        ingestion_report=RepositoryIngestionReport(
            failures=[RepositoryIngestionFailure(path="README.md", reason="copy failed")]
        ),
    )

    summary = RepositoryObjectiveSummaryBuilder().build_from_incremental_reports(
        "Failed Incremental Objective",
        [report],
    )

    assert summary.total_failures == 1
    assert summary.action_required is True
    assert summary.status == "attention_required"


def test_objective_summary_counts_duplicate_files():
    report = RepositoryIngestionReport(
        duplicate_count=2,
        duplicate_files=[
            RepositoryDuplicateFile(path="README.md"),
            RepositoryDuplicateFile(path="PLAN.md"),
        ],
    )

    summary = RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
        "Duplicate Objective",
        [report],
    )

    assert summary.total_duplicates == 2
    assert summary.action_required is False


def test_objective_summary_is_complete_false_when_action_required_even_if_named_complete():
    report = RepositoryIngestionReport(
        document_count=1,
        failures=[RepositoryIngestionFailure(path="bad.md", reason="copy failed")],
    )

    summary = RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
        "Attention Objective",
        [report],
    )

    assert summary.status == "attention_required"
    assert summary.is_complete is False


def test_objective_summary_preserves_objective_name():
    summary = RepositoryObjectiveSummaryBuilder().build_from_ingestion_reports(
        "Custom Objective Name",
        [],
    )

    assert summary.objective_name == "Custom Objective Name"
