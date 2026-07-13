from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_snapshot_comparison import (
    RepositorySnapshotComparison,
)


@dataclass(frozen=True)
class RepositorySnapshotComparisonSummary:
    outcome: str
    message: str
    action_required: bool


class RepositorySnapshotComparisonSummaryBuilder:
    def build(
        self,
        comparison: RepositorySnapshotComparison,
    ) -> RepositorySnapshotComparisonSummary:
        if not comparison.has_changes:
            return RepositorySnapshotComparisonSummary(
                outcome="identical",
                message=(
                    "Repository intelligence snapshots are identical."
                ),
                action_required=False,
            )

        if (
            comparison.critical_delta > 0
            or comparison.warning_delta > 0
            or comparison.decreased_metric_count > 0
            or comparison.removed_metric_count > 0
        ):
            return RepositorySnapshotComparisonSummary(
                outcome="attention_required",
                message=(
                    f"Repository snapshots differ across "
                    f"{comparison.metric_change_count} tracked metric(s). "
                    f"{comparison.decreased_metric_count} metric(s) decreased, "
                    f"{comparison.removed_metric_count} metric(s) were removed, "
                    f"warning delta is {comparison.warning_delta}, and "
                    f"critical delta is {comparison.critical_delta}."
                ),
                action_required=True,
            )

        return RepositorySnapshotComparisonSummary(
            outcome="changed",
            message=(
                f"Repository snapshots changed: "
                f"{comparison.increased_metric_count} metric(s) increased, "
                f"{comparison.added_metric_count} metric(s) were added, "
                f"node delta is {comparison.node_delta}, and "
                f"edge delta is {comparison.edge_delta}."
            ),
            action_required=False,
        )
