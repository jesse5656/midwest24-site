from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_certificate_verification import (
    RepositoryReleaseCertificateVerification,
)


@dataclass(frozen=True)
class RepositoryReleaseCertificateVerificationSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseCertificateVerificationSummaryBuilder:
    def build(
        self,
        verification: RepositoryReleaseCertificateVerification,
    ) -> RepositoryReleaseCertificateVerificationSummary:
        if verification.accepted:
            return RepositoryReleaseCertificateVerificationSummary(
                outcome="certificate_accepted",
                message=(
                    f"Release certificate "
                    f"{verification.certificate_id[:12]} for "
                    f"{verification.repository_name} is valid and "
                    f"certified."
                ),
                action_required=False,
            )

        if verification.critical_issue_count > 0:
            return RepositoryReleaseCertificateVerificationSummary(
                outcome="certificate_rejected_critical",
                message=(
                    f"Release certificate verification failed with "
                    f"{verification.issue_count} issue(s), including "
                    f"{verification.critical_issue_count} critical."
                ),
                action_required=True,
            )

        if verification.valid and not verification.certified:
            return RepositoryReleaseCertificateVerificationSummary(
                outcome="certificate_valid_not_certified",
                message=(
                    "Release certificate integrity is valid, but the "
                    "release is not certified."
                ),
                action_required=True,
            )

        return RepositoryReleaseCertificateVerificationSummary(
            outcome="certificate_rejected",
            message=(
                f"Release certificate verification failed with "
                f"{verification.issue_count} issue(s)."
            ),
            action_required=True,
        )
