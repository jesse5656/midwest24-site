from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.incremental_report import RepositoryIncrementalIngestionReport
from app.connectors.repository.ingestion_report import RepositoryIngestionReport


@dataclass(frozen=True)
class RepositoryObjectiveSummary:
    objective_name: str
    status: str
    total_documents: int
    total_processing_jobs: int
    total_failures: int
    total_duplicates: int
    total_unsupported: int
    total_skipped: int
    action_required: bool

    @property
    def is_complete(self) -> bool:
        return self.status == "complete" and not self.action_required


class RepositoryObjectiveSummaryBuilder:
    def build_from_ingestion_reports(
        self,
        objective_name: str,
        reports: list[RepositoryIngestionReport],
    ) -> RepositoryObjectiveSummary:
        total_documents = sum(report.document_count for report in reports)
        total_processing_jobs = sum(report.processing_job_count for report in reports)
        total_failures = sum(len(report.failures) for report in reports)
        total_duplicates = sum(report.duplicate_count for report in reports)
        total_unsupported = sum(report.unsupported_count for report in reports)
        total_skipped = sum(report.skipped_count for report in reports)

        action_required = total_failures > 0
        status = "attention_required" if action_required else "complete"

        return RepositoryObjectiveSummary(
            objective_name=objective_name,
            status=status,
            total_documents=total_documents,
            total_processing_jobs=total_processing_jobs,
            total_failures=total_failures,
            total_duplicates=total_duplicates,
            total_unsupported=total_unsupported,
            total_skipped=total_skipped,
            action_required=action_required,
        )

    def build_from_incremental_reports(
        self,
        objective_name: str,
        reports: list[RepositoryIncrementalIngestionReport],
    ) -> RepositoryObjectiveSummary:
        ingestion_reports = [
            report.ingestion_report
            for report in reports
            if report.ingestion_report is not None
        ]

        return self.build_from_ingestion_reports(
            objective_name=objective_name,
            reports=ingestion_reports,
        )
