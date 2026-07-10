from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
    RepositorySnapshotBaselineVerification,
)


@dataclass(frozen=True)
class RepositorySnapshotBaselineSummary:
    outcome: str
    message: str
    action_required: bool


class RepositorySnapshotBaselineSummaryBuilder:
    def build_baseline(
        self,
        baseline: RepositorySnapshotBaseline,
    ) -> RepositorySnapshotBaselineSummary:
        if baseline.metric_count == 0:
            return RepositorySnapshotBaselineSummary(
                outcome="empty_baseline",
                message=(
                    "Repository snapshot baseline contains no metrics."
                ),
                action_required=True,
            )

        return RepositorySnapshotBaselineSummary(
            outcome="baseline_created",
            message=(
                f"Repository snapshot baseline created for "
                f"{baseline.repository_name} with "
                f"{baseline.metric_count} metric(s) and fingerprint "
                f"{baseline.fingerprint[:12]}."
            ),
            action_required=False,
        )

    def build_verification(
        self,
        verification: RepositorySnapshotBaselineVerification,
    ) -> RepositorySnapshotBaselineSummary:
        if verification.matches:
            return RepositorySnapshotBaselineSummary(
                outcome="baseline_match",
                message=(
                    "Repository matches the supplied snapshot baseline."
                ),
                action_required=False,
            )

        return RepositorySnapshotBaselineSummary(
            outcome="baseline_mismatch",
            message=(
                f"Repository does not match the supplied baseline. "
                f"Fingerprint match: "
                f"{verification.fingerprint_matches}. "
                f"Detected {verification.difference_count} "
                f"difference(s)."
            ),
            action_required=True,
        )
