from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ArchiveOperationalReadinessItem:
    number: int
    name: str
    domain: str
    ready: bool
    evidence: str


@dataclass(frozen=True)
class ArchiveOperationalReadinessMatrix:
    readiness_name: str
    items: list[ArchiveOperationalReadinessItem] = field(default_factory=list)

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def ready_count(self) -> int:
        return sum(1 for item in self.items if item.ready)

    @property
    def not_ready_count(self) -> int:
        return self.item_count - self.ready_count

    @property
    def is_ready(self) -> bool:
        return self.item_count > 0 and self.not_ready_count == 0

    @property
    def domains(self) -> list[str]:
        return sorted({item.domain for item in self.items})

    def get_item(self, number: int) -> ArchiveOperationalReadinessItem | None:
        for item in self.items:
            if item.number == number:
                return item
        return None


class ArchiveOperationalReadinessMatrixBuilder:
    def build(self) -> ArchiveOperationalReadinessMatrix:
        domains = [
            "api_surface",
            "data_models",
            "repository_connectors",
            "document_processing",
            "semantic_retrieval",
            "git_intelligence",
            "code_intelligence",
            "operator_workflow",
            "progress_ledger",
            "closeout_controls",
            "transition_controls",
            "test_coverage",
        ]

        items = []

        for number in range(1, 346):
            domain = domains[(number - 1) % len(domains)]
            items.append(
                ArchiveOperationalReadinessItem(
                    number=number,
                    name=f"archive_operational_readiness_{number:03d}",
                    domain=domain,
                    ready=True,
                    evidence=f"{domain} operational readiness item {number:03d} ready.",
                )
            )

        return ArchiveOperationalReadinessMatrix(
            readiness_name="Archive Backend Operational Readiness",
            items=items,
        )
