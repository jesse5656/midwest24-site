from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_snapshot_gate import (
    RepositorySnapshotGateResult,
)


@dataclass(frozen=True)
class RepositorySnapshotGateSummary:
    outcome: str
    message: str
    action_required: bool


class RepositorySnapshotGateSummaryBuilder:
    def build(
        self,
        result: RepositorySnapshotGateResult,
    ) -> RepositorySnapshotGateSummary:
        if result.passed:
            return RepositorySnapshotGateSummary(
                outcome="gate_passed",
                message=(
                    "Repository snapshot gate passed. "
                    "Baseline verification and policy evaluation succeeded."
                ),
                action_required=False,
            )

        if result.critical_reason_count > 0:
            return RepositorySnapshotGateSummary(
                outcome="gate_blocked_critical",
                message=(
                    f"Repository snapshot gate blocked with "
                    f"{result.reason_count} reason(s), including "
                    f"{result.critical_reason_count} critical reason(s)."
                ),
                action_required=True,
            )

        return RepositorySnapshotGateSummary(
            outcome="gate_blocked",
            message=(
                f"Repository snapshot gate blocked with "
                f"{result.reason_count} reason(s)."
            ),
            action_required=True,
        )
