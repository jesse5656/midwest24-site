from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_dependency_map import RepositoryDependencyMap


@dataclass(frozen=True)
class RepositoryDependencyMapSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryDependencyMapSummaryBuilder:
    def build(self, dependency_map: RepositoryDependencyMap) -> RepositoryDependencyMapSummary:
        if dependency_map.dependency_count == 0:
            return RepositoryDependencyMapSummary(
                outcome="no_dependencies",
                message="Repository dependency map found no dependencies.",
                action_required=False,
            )

        if dependency_map.ecosystem_count == 1:
            return RepositoryDependencyMapSummary(
                outcome="single_ecosystem_dependencies",
                message=(
                    f"Repository dependency map found {dependency_map.dependency_count} "
                    f"dependenc(y/ies) for {dependency_map.ecosystems[0]}."
                ),
                action_required=False,
            )

        return RepositoryDependencyMapSummary(
            outcome="multi_ecosystem_dependencies",
            message=(
                f"Repository dependency map found {dependency_map.dependency_count} "
                f"dependenc(y/ies) across {dependency_map.ecosystem_count} ecosystem(s)."
            ),
            action_required=False,
        )
