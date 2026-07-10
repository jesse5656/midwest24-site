from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_intelligence_report import (
    RepositoryIntelligenceReport,
)


@dataclass(frozen=True)
class RepositoryIntelligenceReportSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryIntelligenceReportSummaryBuilder:
    def build(
        self,
        report: RepositoryIntelligenceReport,
    ) -> RepositoryIntelligenceReportSummary:
        if report.section_count == 0:
            return RepositoryIntelligenceReportSummary(
                outcome="empty_report",
                message=(
                    "Repository intelligence report has no sections."
                ),
                action_required=True,
            )

        if report.critical_count > 0:
            return RepositoryIntelligenceReportSummary(
                outcome="critical_findings",
                message=(
                    f"{report.title} contains "
                    f"{report.section_count} section(s), "
                    f"{report.warning_count} warning section(s), and "
                    f"{report.critical_count} critical section(s)."
                ),
                action_required=True,
            )

        if report.warning_count > 0:
            return RepositoryIntelligenceReportSummary(
                outcome="warnings_detected",
                message=(
                    f"{report.title} contains "
                    f"{report.section_count} section(s) and "
                    f"{report.warning_count} warning section(s)."
                ),
                action_required=True,
            )

        return RepositoryIntelligenceReportSummary(
            outcome="healthy",
            message=(
                f"{report.title} contains "
                f"{report.section_count} healthy section(s)."
            ),
            action_required=False,
        )
