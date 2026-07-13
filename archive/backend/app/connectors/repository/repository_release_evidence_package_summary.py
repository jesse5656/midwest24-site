from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_evidence_package import (
    RepositoryReleaseEvidencePackage,
)


@dataclass(frozen=True)
class RepositoryReleaseEvidencePackageSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseEvidencePackageSummaryBuilder:
    def build(
        self,
        package: RepositoryReleaseEvidencePackage,
    ) -> RepositoryReleaseEvidencePackageSummary:
        if package.accepted:
            return RepositoryReleaseEvidencePackageSummary(
                outcome="release_package_accepted",
                message=(
                    f"{package.repository_name} release evidence "
                    f"package {package.package_id[:12]} was accepted "
                    f"with {package.evidence_count} evidence item(s)."
                ),
                action_required=False,
            )

        return RepositoryReleaseEvidencePackageSummary(
            outcome="release_package_rejected",
            message=(
                f"{package.repository_name} release evidence package "
                f"was rejected because "
                f"{package.failed_component_count} component(s) failed."
            ),
            action_required=True,
        )
