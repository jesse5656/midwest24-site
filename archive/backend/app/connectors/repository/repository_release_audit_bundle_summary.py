from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_audit_bundle import (
    RepositoryReleaseAuditBundle,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditBundleSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditBundleSummaryBuilder:
    def build(
        self,
        bundle: RepositoryReleaseAuditBundle,
    ) -> RepositoryReleaseAuditBundleSummary:
        if bundle.accepted:
            return RepositoryReleaseAuditBundleSummary(
                outcome="release_audit_bundle_accepted",
                message=(
                    f"{bundle.repository_name} release audit bundle "
                    f"{bundle.bundle_id[:12]} was accepted."
                ),
                action_required=False,
            )

        return RepositoryReleaseAuditBundleSummary(
            outcome="release_audit_bundle_rejected",
            message=(
                f"{bundle.repository_name} release audit bundle was "
                f"rejected because {bundle.failed_component_count} "
                f"component(s) failed."
            ),
            action_required=True,
        )
