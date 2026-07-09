from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.code_objective_scorecard import CodeObjectiveScorecard


@dataclass(frozen=True)
class CodeObjectiveOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class CodeObjectiveSummaryBuilder:
    def build(self, scorecard: CodeObjectiveScorecard) -> CodeObjectiveOperatorSummary:
        if scorecard.capability_count == 0:
            return CodeObjectiveOperatorSummary(
                outcome="not_started",
                message="Code Intelligence Preview has no recorded capabilities.",
                action_required=True,
            )

        if scorecard.is_complete:
            return CodeObjectiveOperatorSummary(
                outcome="complete",
                message=(
                    f"Code Intelligence Preview is complete with "
                    f"{scorecard.completed_capability_count}/{scorecard.capability_count} capabilities "
                    f"and {scorecard.test_count} passing tests."
                ),
                action_required=False,
            )

        return CodeObjectiveOperatorSummary(
            outcome="incomplete",
            message=(
                f"Code Intelligence Preview has "
                f"{scorecard.completed_capability_count}/{scorecard.capability_count} capabilities complete."
            ),
            action_required=True,
        )
