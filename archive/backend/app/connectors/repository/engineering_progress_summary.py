from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.engineering_progress import EngineeringProgress


@dataclass(frozen=True)
class EngineeringProgressSummary:
    outcome: str
    message: str
    action_required: bool


class EngineeringProgressSummaryBuilder:
    def build(self, progress: EngineeringProgress) -> EngineeringProgressSummary:
        if progress.capability_count == 0:
            return EngineeringProgressSummary(
                outcome="no_capabilities",
                message="No engineering capabilities are tracked.",
                action_required=True,
            )

        if progress.remaining_count == 0 and progress.in_progress_count == 0:
            return EngineeringProgressSummary(
                outcome="complete",
                message=(
                    f"{progress.milestone_name} is complete with "
                    f"{progress.complete_count}/{progress.capability_count} capabilities complete "
                    f"and {progress.test_count} passing tests."
                ),
                action_required=False,
            )

        return EngineeringProgressSummary(
            outcome="in_progress",
            message=(
                f"{progress.milestone_name} is {int(progress.percent_complete * 100)}% complete: "
                f"{progress.complete_count}/{progress.capability_count} capabilities complete, "
                f"{progress.in_progress_count} in progress, "
                f"{progress.remaining_count} remaining, "
                f"{progress.test_count} tests passing."
            ),
            action_required=False,
        )
