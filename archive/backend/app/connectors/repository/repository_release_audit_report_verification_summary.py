from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_audit_report_verification import (
    RepositoryReleaseAuditReportVerification,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditReportVerificationSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditReportVerificationSummaryBuilder:
    def build(
        self,
        verification: RepositoryReleaseAuditReportVerification,
    ) -> RepositoryReleaseAuditReportVerificationSummary:
        if verification.accepted:
            return RepositoryReleaseAuditReportVerificationSummary(
                outcome="release_audit_report_accepted",
                message=(
                    f"Release audit report "
                    f"{verification.report_id[:12]} for "
                    f"{verification.repository_name} is valid "
                    f"and accepted."
                ),
                action_required=False,
            )

        if verification.critical_issue_count > 0:
            return RepositoryReleaseAuditReportVerificationSummary(
                outcome="release_audit_report_rejected_critical",
                message=(
                    f"Release audit report verification failed "
                    f"with {verification.issue_count} issue(s), "
                    f"including "
                    f"{verification.critical_issue_count} critical."
                ),
                action_required=True,
            )

        if verification.valid:
            return RepositoryReleaseAuditReportVerificationSummary(
                outcome="release_audit_report_valid_not_passed",
                message=(
                    "Release audit report integrity is valid, "
                    "but the audit did not pass."
                ),
                action_required=True,
            )

        return RepositoryReleaseAuditReportVerificationSummary(
            outcome="release_audit_report_rejected",
            message=(
                f"Release audit report verification failed "
                f"with {verification.issue_count} issue(s)."
            ),
            action_required=True,
        )
