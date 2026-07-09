from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.incremental_report import RepositoryIncrementalIngestionReport
from app.connectors.repository.ingestion_report import RepositoryIngestionReport


@dataclass(frozen=True)
class RepositoryIngestionOperatorSummary:
    outcome: str
    message: str
    action_required: bool
    has_failures: bool
    has_duplicates: bool
    has_unsupported_files: bool
    has_skipped_paths: bool


class RepositoryIngestionSummaryBuilder:
    def build(self, report: RepositoryIngestionReport) -> RepositoryIngestionOperatorSummary:
        has_failures = len(report.failures) > 0
        has_duplicates = report.duplicate_count > 0
        has_unsupported_files = report.unsupported_count > 0
        has_skipped_paths = report.skipped_count > 0

        if has_failures:
            return RepositoryIngestionOperatorSummary(
                outcome="partial_failure",
                message=(
                    f"Repository ingestion completed with {len(report.failures)} file failure(s), "
                    f"{report.document_count} document(s), and {report.processing_job_count} processing job(s)."
                ),
                action_required=True,
                has_failures=True,
                has_duplicates=has_duplicates,
                has_unsupported_files=has_unsupported_files,
                has_skipped_paths=has_skipped_paths,
            )

        if report.document_count > 0:
            return RepositoryIngestionOperatorSummary(
                outcome="ingested",
                message=(
                    f"Repository ingestion created {report.document_count} document(s) "
                    f"and {report.processing_job_count} processing job(s)."
                ),
                action_required=False,
                has_failures=False,
                has_duplicates=has_duplicates,
                has_unsupported_files=has_unsupported_files,
                has_skipped_paths=has_skipped_paths,
            )

        if has_duplicates and report.discovered_count > 0:
            return RepositoryIngestionOperatorSummary(
                outcome="duplicates_only",
                message=f"Repository ingestion found {report.duplicate_count} duplicate file(s) and created no new documents.",
                action_required=False,
                has_failures=False,
                has_duplicates=True,
                has_unsupported_files=has_unsupported_files,
                has_skipped_paths=has_skipped_paths,
            )

        if report.discovered_count == 0 and (has_unsupported_files or has_skipped_paths):
            return RepositoryIngestionOperatorSummary(
                outcome="nothing_ingested",
                message="Repository ingestion found no supported files to ingest.",
                action_required=False,
                has_failures=False,
                has_duplicates=has_duplicates,
                has_unsupported_files=has_unsupported_files,
                has_skipped_paths=has_skipped_paths,
            )

        return RepositoryIngestionOperatorSummary(
            outcome="nothing_ingested",
            message="Repository ingestion completed without creating documents.",
            action_required=False,
            has_failures=False,
            has_duplicates=has_duplicates,
            has_unsupported_files=has_unsupported_files,
            has_skipped_paths=has_skipped_paths,
        )


@dataclass(frozen=True)
class RepositoryIncrementalOperatorSummary:
    outcome: str
    message: str
    action_required: bool
    changed_count: int
    ingested_document_count: int


class RepositoryIncrementalSummaryBuilder:
    def build(self, report: RepositoryIncrementalIngestionReport) -> RepositoryIncrementalOperatorSummary:
        if report.changed_count == 0:
            return RepositoryIncrementalOperatorSummary(
                outcome="no_changes",
                message="Incremental repository ingestion detected no changes.",
                action_required=False,
                changed_count=0,
                ingested_document_count=0,
            )

        if report.ingestion_report and report.ingestion_report.failures:
            return RepositoryIncrementalOperatorSummary(
                outcome="partial_failure",
                message=(
                    f"Incremental repository ingestion detected {report.changed_count} change(s) "
                    f"and completed with {len(report.ingestion_report.failures)} failure(s)."
                ),
                action_required=True,
                changed_count=report.changed_count,
                ingested_document_count=report.ingested_document_count,
            )

        return RepositoryIncrementalOperatorSummary(
            outcome="changes_ingested",
            message=(
                f"Incremental repository ingestion detected {report.changed_count} change(s) "
                f"and created {report.ingested_document_count} document(s)."
            ),
            action_required=False,
            changed_count=report.changed_count,
            ingested_document_count=report.ingested_document_count,
        )
