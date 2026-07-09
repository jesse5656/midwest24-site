from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.git_objective_scorecard import GitObjectiveScorecard


@dataclass(frozen=True)
class GitObjectiveOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class GitObjectiveSummaryBuilder:
    def build(self, scorecard: GitObjectiveScorecard) -> GitObjectiveOperatorSummary:
        if scorecard.capability_count == 0:
            return GitObjectiveOperatorSummary(
                outcome="not_started",
                message="Git Repository Intelligence has no recorded capabilities.",
                action_required=True,
            )

        if scorecard.is_complete:
            return GitObjectiveOperatorSummary(
                outcome="complete",
                message=(
                    f"Git Repository Intelligence is complete with "
                    f"{scorecard.completed_capability_count}/{scorecard.capability_count} capabilities "
                    f"and {scorecard.test_count} passing tests."
                ),
                action_required=False,
            )

        return GitObjectiveOperatorSummary(
            outcome="incomplete",
            message=(
                f"Git Repository Intelligence has "
                f"{scorecard.completed_capability_count}/{scorecard.capability_count} capabilities complete."
            ),
            action_required=True,
        )
