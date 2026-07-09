from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.operator_progress_target import OperatorProgressPlan


@dataclass(frozen=True)
class OperatorProgressSummary:
    outcome: str
    message: str
    action_required: bool


class OperatorProgressSummaryBuilder:
    def build(self, plan: OperatorProgressPlan) -> OperatorProgressSummary:
        if not plan.target.is_valid:
            return OperatorProgressSummary(
                outcome="invalid_target",
                message="Target test count must be greater than current test count.",
                action_required=True,
            )

        if plan.unreached_count == 0:
            return OperatorProgressSummary(
                outcome="complete",
                message=f"Target of {plan.target.target_test_count} tests has been reached.",
                action_required=False,
            )

        next_milestone = plan.next_milestone
        return OperatorProgressSummary(
            outcome="in_progress",
            message=(
                f"{plan.target.current_test_count} tests are passing; "
                f"{plan.target.remaining_tests} test(s) remain to reach "
                f"{plan.target.target_test_count}. Next milestone: {next_milestone.test_count}."
            ),
            action_required=False,
        )
