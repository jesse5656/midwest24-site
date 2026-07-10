from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_package_map import RepositoryPackageMap


@dataclass(frozen=True)
class RepositoryPackageMapSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryPackageMapSummaryBuilder:
    def build(self, package_map: RepositoryPackageMap) -> RepositoryPackageMapSummary:
        if not package_map.has_package_markers:
            return RepositoryPackageMapSummary(
                outcome="no_package_markers",
                message="Repository package map found no package or dependency markers.",
                action_required=False,
            )

        if package_map.ecosystem_count == 1:
            return RepositoryPackageMapSummary(
                outcome="single_ecosystem",
                message=(
                    f"Repository package map found {package_map.marker_count} marker(s) "
                    f"for {package_map.ecosystems[0]}."
                ),
                action_required=False,
            )

        return RepositoryPackageMapSummary(
            outcome="multi_ecosystem",
            message=(
                f"Repository package map found {package_map.marker_count} marker(s) "
                f"across {package_map.ecosystem_count} ecosystem(s)."
            ),
            action_required=False,
        )
