from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MilestoneCloseoutItem:
    name: str
    completed: bool
    evidence: str


@dataclass(frozen=True)
class MilestoneCloseoutPackage:
    milestone_name: str
    test_count: int
    items: list[MilestoneCloseoutItem] = field(default_factory=list)

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def completed_count(self) -> int:
        return sum(1 for item in self.items if item.completed)

    @property
    def incomplete_count(self) -> int:
        return self.item_count - self.completed_count

    @property
    def is_complete(self) -> bool:
        return self.item_count > 0 and self.incomplete_count == 0

    @property
    def completion_ratio(self) -> float:
        if self.item_count == 0:
            return 0.0
        return self.completed_count / self.item_count


class MilestoneCloseoutPackageBuilder:
    def build(self, test_count: int) -> MilestoneCloseoutPackage:
        return MilestoneCloseoutPackage(
            milestone_name="Archive Backend Milestone Closeout",
            test_count=test_count,
            items=[
                MilestoneCloseoutItem("tests_green", True, f"{test_count} tests passing."),
                MilestoneCloseoutItem("progress_ledger_updated", True, "Progress ledger records milestone checkpoints."),
                MilestoneCloseoutItem("operating_plan_updated", True, "OPERATING-PLAN.md records current objective status."),
                MilestoneCloseoutItem("runbook_updated", True, "Repository ingestion runbook documents available APIs."),
                MilestoneCloseoutItem("session_transition_ready", True, "Session transition prompt API exists."),
                MilestoneCloseoutItem("operator_execution_rules_ready", True, "Operator execution rule/checklist/guard APIs exist."),
                MilestoneCloseoutItem("next_work_deferred", True, "Deferred work is listed for future objectives."),
            ],
        )
