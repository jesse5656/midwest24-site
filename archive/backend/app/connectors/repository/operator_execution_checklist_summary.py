from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.operator_execution_checklist import OperatorExecutionChecklist


@dataclass(frozen=True)
class OperatorExecutionChecklistSummary:
    outcome: str
    message: str
    action_required: bool


class OperatorExecutionChecklistSummaryBuilder:
    def build(self, checklist: OperatorExecutionChecklist) -> OperatorExecutionChecklistSummary:
        if checklist.item_count == 0:
            return OperatorExecutionChecklistSummary(
                outcome="empty_checklist",
                message="Operator execution checklist has no items.",
                action_required=True,
            )

        if checklist.is_complete:
            return OperatorExecutionChecklistSummary(
                outcome="complete",
                message=(
                    f"{checklist.name} is complete with "
                    f"{checklist.completed_count}/{checklist.item_count} item(s)."
                ),
                action_required=False,
            )

        return OperatorExecutionChecklistSummary(
            outcome="incomplete",
            message=(
                f"{checklist.name} has "
                f"{checklist.completed_count}/{checklist.item_count} completed item(s)."
            ),
            action_required=True,
        )
