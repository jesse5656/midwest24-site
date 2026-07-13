from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_certification import (
    RepositoryReleaseCertification,
)


@dataclass(frozen=True)
class RepositoryReleaseCertificationSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseCertificationSummaryBuilder:
    def build(
        self,
        certification: RepositoryReleaseCertification,
    ) -> RepositoryReleaseCertificationSummary:
        if certification.certified:
            return RepositoryReleaseCertificationSummary(
                outcome="release_certified",
                message=(
                    f"{certification.repository_name} received release "
                    f"certification {certification.certificate_id[:12]} "
                    f"with {certification.evidence_count} evidence item(s)."
                ),
                action_required=False,
            )

        if certification.critical_failure_count > 0:
            return RepositoryReleaseCertificationSummary(
                outcome="certification_denied_critical",
                message=(
                    f"{certification.repository_name} was denied release "
                    f"certification due to "
                    f"{certification.critical_failure_count} critical "
                    f"failure(s)."
                ),
                action_required=True,
            )

        return RepositoryReleaseCertificationSummary(
            outcome="certification_denied",
            message=(
                f"{certification.repository_name} was denied release "
                f"certification with "
                f"{certification.denial_reason_count} denial reason(s)."
            ),
            action_required=True,
        )
