from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BackendMilestoneCapability:
    name: str
    completed: bool
    evidence: str


@dataclass(frozen=True)
class BackendMilestoneScorecard:
    milestone_name: str
    test_count: int
    capabilities: list[BackendMilestoneCapability] = field(default_factory=list)

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


class BackendMilestoneScorecardBuilder:
    def build(self, test_count: int) -> BackendMilestoneScorecard:
        return BackendMilestoneScorecard(
            milestone_name="Archive Backend Milestone",
            test_count=test_count,
            capabilities=[
                BackendMilestoneCapability("entity_api", True, "Entity API exists."),
                BackendMilestoneCapability("documents_pipeline", True, "Documents, jobs, worker, chunks, embeddings, and semantic search exist."),
                BackendMilestoneCapability("repository_ingestion", True, "Repository ingestion and incremental ingestion exist."),
                BackendMilestoneCapability("git_intelligence", True, "Git intelligence APIs and reports exist."),
                BackendMilestoneCapability("code_intelligence", True, "Code inventory, outline, and code intelligence report exist."),
                BackendMilestoneCapability("progress_tracking", True, "Progress ledger exists."),
                BackendMilestoneCapability("backend_health", True, "Backend health API exists."),
            ],
        )
