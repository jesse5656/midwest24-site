from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_audit_bundle_verification import (
    RepositoryReleaseAuditBundleVerification,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditBundleVerificationSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditBundleVerificationSummaryBuilder:
    def build(
        self,
        verification: RepositoryReleaseAuditBundleVerification,
    ) -> RepositoryReleaseAuditBundleVerificationSummary:
        if verification.accepted:
            return RepositoryReleaseAuditBundleVerificationSummary(
                outcome="release_audit_bundle_accepted",
                message=(
                    f"Release audit bundle "
                    f"{verification.bundle_id[:12]} for "
                    f"{verification.repository_name} is valid and "
                    f"accepted."
                ),
                action_required=False,
            )

        if verification.critical_issue_count > 0:
            return RepositoryReleaseAuditBundleVerificationSummary(
                outcome="release_audit_bundle_rejected_critical",
                message=(
                    f"Release audit bundle verification failed with "
                    f"{verification.issue_count} issue(s), including "
                    f"{verification.critical_issue_count} critical."
                ),
                action_required=True,
            )

        if verification.valid:
            return RepositoryReleaseAuditBundleVerificationSummary(
                outcome="release_audit_bundle_valid_not_accepted",
                message=(
                    "Release audit bundle integrity is valid, but "
                    "the bundle is not accepted."
                ),
                action_required=True,
            )

        return RepositoryReleaseAuditBundleVerificationSummary(
            outcome="release_audit_bundle_rejected",
            message=(
                f"Release audit bundle verification failed with "
                f"{verification.issue_count} issue(s)."
            ),
            action_required=True,
        )
