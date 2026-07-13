from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_attestation import (
    RepositoryReleaseAttestation,
)


@dataclass(frozen=True)
class RepositoryReleaseAttestationSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAttestationSummaryBuilder:
    def build(
        self,
        attestation: RepositoryReleaseAttestation,
    ) -> RepositoryReleaseAttestationSummary:
        if attestation.accepted:
            return RepositoryReleaseAttestationSummary(
                outcome="attestation_accepted",
                message=(
                    f"{attestation.repository_name} release attestation "
                    f"{attestation.attestation_id[:12]} was accepted with "
                    f"{attestation.evidence_count} evidence item(s)."
                ),
                action_required=False,
            )

        if not attestation.certificate_valid:
            return RepositoryReleaseAttestationSummary(
                outcome="attestation_rejected_invalid_certificate",
                message=(
                    f"{attestation.repository_name} release attestation "
                    f"was rejected because its certificate is invalid."
                ),
                action_required=True,
            )

        return RepositoryReleaseAttestationSummary(
            outcome="attestation_rejected",
            message=(
                f"{attestation.repository_name} release attestation "
                f"was rejected with {attestation.failed_evidence_count} "
                f"failed evidence item(s) and "
                f"{attestation.issue_count} verification issue(s)."
            ),
            action_required=True,
        )
