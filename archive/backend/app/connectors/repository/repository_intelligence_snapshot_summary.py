from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshot,
)


@dataclass(frozen=True)
class RepositoryIntelligenceSnapshotSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryIntelligenceSnapshotSummaryBuilder:
    def build(
        self,
        snapshot: RepositoryIntelligenceSnapshot,
    ) -> RepositoryIntelligenceSnapshotSummary:
        if snapshot.metric_count == 0:
            return RepositoryIntelligenceSnapshotSummary(
                outcome="empty_snapshot",
                message=(
                    "Repository intelligence snapshot contains no metrics."
                ),
                action_required=True,
            )

        if snapshot.critical_count > 0:
            return RepositoryIntelligenceSnapshotSummary(
                outcome="critical",
                message=(
                    f"{snapshot.repository_name} snapshot contains "
                    f"{snapshot.metric_count} metric(s) and "
                    f"{snapshot.critical_count} critical finding(s)."
                ),
                action_required=True,
            )

        if snapshot.warning_count > 0:
            return RepositoryIntelligenceSnapshotSummary(
                outcome="warnings_detected",
                message=(
                    f"{snapshot.repository_name} snapshot contains "
                    f"{snapshot.metric_count} metric(s) and "
                    f"{snapshot.warning_count} warning(s)."
                ),
                action_required=True,
            )

        return RepositoryIntelligenceSnapshotSummary(
            outcome="healthy",
            message=(
                f"{snapshot.repository_name} snapshot contains "
                f"{snapshot.metric_count} metric(s), "
                f"{snapshot.node_count} graph node(s), and fingerprint "
                f"{snapshot.fingerprint[:12]}."
            ),
            action_required=False,
        )
