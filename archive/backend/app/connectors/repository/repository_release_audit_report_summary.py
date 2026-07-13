from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_audit_report import (
    RepositoryReleaseAuditReport,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditReportSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditReportSummaryBuilder:
    def build(
        self,
        report: RepositoryReleaseAuditReport,
    ) -> RepositoryReleaseAuditReportSummary:
        if report.passed:
            return RepositoryReleaseAuditReportSummary(
                outcome="release_audit_passed",
                message=(
                    f"{report.repository_name} release audit "
                    f"{report.report_id[:12]} passed with "
                    f"{report.finding_count} finding(s)."
                ),
                action_required=False,
            )

        if report.critical_finding_count > 0:
            return RepositoryReleaseAuditReportSummary(
                outcome="release_audit_failed_critical",
                message=(
                    f"{report.repository_name} release audit failed "
                    f"with {report.finding_count} finding(s), including "
                    f"{report.critical_finding_count} critical."
                ),
                action_required=True,
            )

        return RepositoryReleaseAuditReportSummary(
            outcome="release_audit_failed",
            message=(
                f"{report.repository_name} release audit failed "
                f"with {report.finding_count} finding(s)."
            ),
            action_required=True,
        )
