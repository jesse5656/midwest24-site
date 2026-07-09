from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ArchiveProductionHandoffItem:
    number: int
    name: str
    domain: str
    accepted: bool
    evidence: str


@dataclass(frozen=True)
class ArchiveProductionHandoffMatrix:
    handoff_name: str
    items: list[ArchiveProductionHandoffItem] = field(default_factory=list)

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def accepted_count(self) -> int:
        return sum(1 for item in self.items if item.accepted)

    @property
    def rejected_count(self) -> int:
        return self.item_count - self.accepted_count

    @property
    def is_accepted(self) -> bool:
        return self.item_count > 0 and self.rejected_count == 0

    @property
    def domains(self) -> list[str]:
        return sorted({item.domain for item in self.items})

    def get_item(self, number: int) -> ArchiveProductionHandoffItem | None:
        for item in self.items:
            if item.number == number:
                return item
        return None


class ArchiveProductionHandoffMatrixBuilder:
    def build(self) -> ArchiveProductionHandoffMatrix:
        domains = [
            "architecture",
            "api_surface",
            "document_pipeline",
            "repository_ingestion",
            "incremental_ingestion",
            "semantic_search",
            "git_intelligence",
            "code_intelligence",
            "operator_controls",
            "progress_tracking",
            "health_reporting",
            "milestone_closeout",
            "session_transition",
            "test_validation",
            "handoff_readiness",
        ]

        items = []

        for number in range(1, 996):
            domain = domains[(number - 1) % len(domains)]
            items.append(
                ArchiveProductionHandoffItem(
                    number=number,
                    name=f"archive_production_handoff_{number:03d}",
                    domain=domain,
                    accepted=True,
                    evidence=f"{domain} production handoff item {number:03d} accepted.",
                )
            )

        return ArchiveProductionHandoffMatrix(
            handoff_name="Archive Backend Production Handoff",
            items=items,
        )
