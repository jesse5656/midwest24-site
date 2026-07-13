from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_evidence_package_verification import (
    RepositoryReleaseEvidencePackageVerification,
)


@dataclass(frozen=True)
class RepositoryReleaseEvidencePackageVerificationSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseEvidencePackageVerificationSummaryBuilder:
    def build(
        self,
        verification: RepositoryReleaseEvidencePackageVerification,
    ) -> RepositoryReleaseEvidencePackageVerificationSummary:
        if verification.accepted:
            return RepositoryReleaseEvidencePackageVerificationSummary(
                outcome="release_package_accepted",
                message=(
                    f"Release evidence package "
                    f"{verification.package_id[:12]} for "
                    f"{verification.repository_name} is valid and "
                    f"accepted."
                ),
                action_required=False,
            )

        if verification.critical_issue_count > 0:
            return RepositoryReleaseEvidencePackageVerificationSummary(
                outcome="release_package_rejected_critical",
                message=(
                    f"Release evidence package verification failed "
                    f"with {verification.issue_count} issue(s), "
                    f"including "
                    f"{verification.critical_issue_count} critical."
                ),
                action_required=True,
            )

        if verification.valid:
            return RepositoryReleaseEvidencePackageVerificationSummary(
                outcome="release_package_valid_not_accepted",
                message=(
                    "Release evidence package integrity is valid, "
                    "but the package is not accepted."
                ),
                action_required=True,
            )

        return RepositoryReleaseEvidencePackageVerificationSummary(
            outcome="release_package_rejected",
            message=(
                f"Release evidence package verification failed "
                f"with {verification.issue_count} issue(s)."
            ),
            action_required=True,
        )
