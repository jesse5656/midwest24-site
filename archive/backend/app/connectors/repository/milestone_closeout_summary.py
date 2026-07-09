from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.milestone_closeout_package import MilestoneCloseoutPackage


@dataclass(frozen=True)
class MilestoneCloseoutSummary:
    outcome: str
    message: str
    action_required: bool


class MilestoneCloseoutSummaryBuilder:
    def build(self, package: MilestoneCloseoutPackage) -> MilestoneCloseoutSummary:
        if package.item_count == 0:
            return MilestoneCloseoutSummary(
                outcome="empty_closeout",
                message="Milestone closeout package has no items.",
                action_required=True,
            )

        if package.is_complete:
            return MilestoneCloseoutSummary(
                outcome="ready_to_close",
                message=(
                    f"{package.milestone_name} is ready to close with "
                    f"{package.completed_count}/{package.item_count} item(s) complete "
                    f"and {package.test_count} passing tests."
                ),
                action_required=False,
            )

        return MilestoneCloseoutSummary(
            outcome="not_ready",
            message=(
                f"{package.milestone_name} has "
                f"{package.incomplete_count} incomplete closeout item(s)."
            ),
            action_required=True,
        )
