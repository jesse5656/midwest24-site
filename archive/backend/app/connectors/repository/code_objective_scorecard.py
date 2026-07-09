from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CodeObjectiveCapability:
    name: str
    completed: bool
    evidence: str


@dataclass(frozen=True)
class CodeObjectiveScorecard:
    objective_name: str
    capabilities: list[CodeObjectiveCapability] = field(default_factory=list)
    test_count: int = 0

    @property
    def capability_count(self) -> int:
        return len(self.capabilities)

    @property
    def completed_capability_count(self) -> int:
        return sum(1 for capability in self.capabilities if capability.completed)

    @property
    def incomplete_capability_count(self) -> int:
        return self.capability_count - self.completed_capability_count

    @property
    def completion_ratio(self) -> float:
        if self.capability_count == 0:
            return 0.0
        return self.completed_capability_count / self.capability_count

    @property
    def is_complete(self) -> bool:
        return self.capability_count > 0 and self.incomplete_capability_count == 0


class CodeObjectiveScorecardBuilder:
    def build(self, test_count: int) -> CodeObjectiveScorecard:
        return CodeObjectiveScorecard(
            objective_name="Code Intelligence Preview",
            test_count=test_count,
            capabilities=[
                CodeObjectiveCapability("code_inventory_api", True, "Repository code inventory endpoint exists."),
                CodeObjectiveCapability("source_outline_api", True, "Source outline preview endpoint exists."),
                CodeObjectiveCapability("code_intelligence_report_api", True, "Combined code intelligence report endpoint exists."),
                CodeObjectiveCapability("readiness_closeout", True, "Code intelligence readiness and closeout primitives exist."),
                CodeObjectiveCapability("progress_ledger", True, "Progress ledger tracks objective checkpoints."),
            ],
        )
