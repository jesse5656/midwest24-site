from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.backend_milestone import BackendMilestoneScorecard


@dataclass(frozen=True)
class BackendMilestoneOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class BackendMilestoneSummaryBuilder:
    def build(self, scorecard: BackendMilestoneScorecard) -> BackendMilestoneOperatorSummary:
        if scorecard.capability_count == 0:
            return BackendMilestoneOperatorSummary(
                outcome="not_started",
                message="Archive Backend Milestone has no recorded capabilities.",
                action_required=True,
            )

        if scorecard.is_complete:
            return BackendMilestoneOperatorSummary(
                outcome="complete",
                message=(
                    f"Archive Backend Milestone is complete with "
                    f"{scorecard.completed_capability_count}/{scorecard.capability_count} capabilities "
                    f"and {scorecard.test_count} passing tests."
                ),
                action_required=False,
            )

        return BackendMilestoneOperatorSummary(
            outcome="incomplete",
            message=(
                f"Archive Backend Milestone has "
                f"{scorecard.completed_capability_count}/{scorecard.capability_count} capabilities complete."
            ),
            action_required=True,
        )
