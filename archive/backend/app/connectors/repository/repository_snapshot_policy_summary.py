from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicyEvaluation,
)


@dataclass(frozen=True)
class RepositorySnapshotPolicySummary:
    outcome: str
    message: str
    action_required: bool


class RepositorySnapshotPolicySummaryBuilder:
    def build(
        self,
        evaluation: RepositorySnapshotPolicyEvaluation,
    ) -> RepositorySnapshotPolicySummary:
        if evaluation.passed:
            return RepositorySnapshotPolicySummary(
                outcome="policy_passed",
                message=(
                    "Repository satisfies the supplied snapshot policy."
                ),
                action_required=False,
            )

        if evaluation.critical_violation_count > 0:
            return RepositorySnapshotPolicySummary(
                outcome="critical_policy_failure",
                message=(
                    f"Repository failed snapshot policy with "
                    f"{evaluation.violation_count} violation(s), "
                    f"including "
                    f"{evaluation.critical_violation_count} critical."
                ),
                action_required=True,
            )

        return RepositorySnapshotPolicySummary(
            outcome="policy_failed",
            message=(
                f"Repository failed snapshot policy with "
                f"{evaluation.violation_count} violation(s)."
            ),
            action_required=True,
        )
