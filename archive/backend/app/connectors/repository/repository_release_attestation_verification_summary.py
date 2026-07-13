from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_attestation_verification import (
    RepositoryReleaseAttestationVerification,
)


@dataclass(frozen=True)
class RepositoryReleaseAttestationVerificationSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAttestationVerificationSummaryBuilder:
    def build(
        self,
        verification: RepositoryReleaseAttestationVerification,
    ) -> RepositoryReleaseAttestationVerificationSummary:
        if verification.accepted:
            return RepositoryReleaseAttestationVerificationSummary(
                outcome="attestation_accepted",
                message=(
                    f"Release attestation "
                    f"{verification.attestation_id[:12]} for "
                    f"{verification.repository_name} is valid and "
                    f"accepted."
                ),
                action_required=False,
            )

        if verification.critical_issue_count > 0:
            return RepositoryReleaseAttestationVerificationSummary(
                outcome="attestation_rejected_critical",
                message=(
                    f"Release attestation verification failed with "
                    f"{verification.issue_count} issue(s), including "
                    f"{verification.critical_issue_count} critical."
                ),
                action_required=True,
            )

        if verification.valid:
            return RepositoryReleaseAttestationVerificationSummary(
                outcome="attestation_valid_not_accepted",
                message=(
                    "Release attestation integrity is valid, but the "
                    "attestation is not accepted."
                ),
                action_required=True,
            )

        return RepositoryReleaseAttestationVerificationSummary(
            outcome="attestation_rejected",
            message=(
                f"Release attestation verification failed with "
                f"{verification.issue_count} issue(s)."
            ),
            action_required=True,
        )
