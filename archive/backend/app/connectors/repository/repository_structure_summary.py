from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_structure import RepositoryStructureReport


@dataclass(frozen=True)
class RepositoryStructureSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryStructureSummaryBuilder:
    def build(self, report: RepositoryStructureReport) -> RepositoryStructureSummary:
        if report.node_count == 0:
            return RepositoryStructureSummary(
                outcome="empty_repository",
                message="Repository structure scan found no visible files or directories.",
                action_required=False,
            )

        return RepositoryStructureSummary(
            outcome="structure_detected",
            message=(
                f"Repository structure scan found {report.directory_count} directorie(s), "
                f"{report.file_count} file(s), and max depth {report.max_depth}."
            ),
            action_required=False,
        )
