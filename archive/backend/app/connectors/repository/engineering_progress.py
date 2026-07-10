from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EngineeringCapability:
    name: str
    status: str
    evidence: str = ""

    @property
    def is_complete(self) -> bool:
        return self.status == "complete"

    @property
    def is_in_progress(self) -> bool:
        return self.status == "in_progress"

    @property
    def is_remaining(self) -> bool:
        return self.status == "remaining"


@dataclass(frozen=True)
class EngineeringProgress:
    milestone_name: str
    test_count: int
    capabilities: list[EngineeringCapability] = field(default_factory=list)

    @property
    def capability_count(self) -> int:
        return len(self.capabilities)

    @property
    def complete_count(self) -> int:
        return sum(1 for capability in self.capabilities if capability.is_complete)

    @property
    def in_progress_count(self) -> int:
        return sum(1 for capability in self.capabilities if capability.is_in_progress)

    @property
    def remaining_count(self) -> int:
        return sum(1 for capability in self.capabilities if capability.is_remaining)

    @property
    def percent_complete(self) -> float:
        if self.capability_count == 0:
            return 0.0
        return round(self.complete_count / self.capability_count, 4)

    @property
    def completed_capabilities(self) -> list[EngineeringCapability]:
        return [capability for capability in self.capabilities if capability.is_complete]

    @property
    def in_progress_capabilities(self) -> list[EngineeringCapability]:
        return [capability for capability in self.capabilities if capability.is_in_progress]

    @property
    def remaining_capabilities(self) -> list[EngineeringCapability]:
        return [capability for capability in self.capabilities if capability.is_remaining]


class EngineeringProgressBuilder:
    def build(self, test_count: int = 3208) -> EngineeringProgress:
        return EngineeringProgress(
            milestone_name="Repository Intelligence Engine",
            test_count=test_count,
            capabilities=[
                EngineeringCapability("Repository Structure", "complete", "Repository structure API exists."),
                EngineeringCapability("Package Map", "complete", "Repository package marker API exists."),
                EngineeringCapability("Dependency Map", "complete", "Repository dependency map API exists."),
                EngineeringCapability("Import Graph", "complete", "Repository import graph API exists."),
                EngineeringCapability("Symbol Index", "complete", "Repository symbol index API exists."),
                EngineeringCapability("Cross Reference Graph", "complete", "Repository cross-reference graph API exists."),
                EngineeringCapability("Knowledge Graph", "in_progress", "Repository knowledge graph is the next integration layer."),
                EngineeringCapability("Semantic Code Search", "remaining", "Code-aware semantic query layer not complete."),
                EngineeringCapability("Architecture Report", "remaining", "Architecture report generator not complete."),
                EngineeringCapability("Repository Summary", "remaining", "Repository summary generator not complete."),
                EngineeringCapability("Drift Detection", "remaining", "Architecture drift detection not complete."),
            ],
        )
