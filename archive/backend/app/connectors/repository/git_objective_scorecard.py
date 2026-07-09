from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GitObjectiveCapability:
    name: str
    completed: bool
    evidence: str


@dataclass(frozen=True)
class GitObjectiveScorecard:
    objective_name: str
    capabilities: list[GitObjectiveCapability] = field(default_factory=list)
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


class GitObjectiveScorecardBuilder:
    def build(self, test_count: int) -> GitObjectiveScorecard:
        return GitObjectiveScorecard(
            objective_name="Git Repository Intelligence",
            test_count=test_count,
            capabilities=[
                GitObjectiveCapability("repository_intelligence_api", True, "Repository metadata endpoint exists."),
                GitObjectiveCapability("commit_preview_api", True, "Commit preview endpoint exists."),
                GitObjectiveCapability("file_change_preview_api", True, "File-change preview endpoint exists."),
                GitObjectiveCapability("authorship_preview_api", True, "Authorship preview endpoint exists."),
                GitObjectiveCapability("branch_analysis_api", True, "Branch analysis endpoint exists."),
                GitObjectiveCapability("combined_report_api", True, "Combined Git intelligence report endpoint exists."),
                GitObjectiveCapability("readiness_closeout", True, "Readiness and closeout primitives exist."),
            ],
        )
