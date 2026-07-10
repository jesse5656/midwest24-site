from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_architecture_report import RepositoryArchitectureReport


@dataclass(frozen=True)
class RepositoryArchitectureReportSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryArchitectureReportSummaryBuilder:
    def build(self, report: RepositoryArchitectureReport) -> RepositoryArchitectureReportSummary:
        if report.finding_count == 0:
            return RepositoryArchitectureReportSummary(
                outcome="empty_report",
                message="Repository architecture report has no findings.",
                action_required=True,
            )

        if report.has_warnings:
            return RepositoryArchitectureReportSummary(
                outcome="warnings_detected",
                message=(
                    f"{report.title} produced {report.finding_count} finding(s), "
                    f"including {report.warning_count} warning(s) and {report.critical_count} critical finding(s)."
                ),
                action_required=True,
            )

        return RepositoryArchitectureReportSummary(
            outcome="healthy",
            message=f"{report.title} produced {report.finding_count} informational finding(s).",
            action_required=False,
        )
