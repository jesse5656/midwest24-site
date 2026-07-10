from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_import_graph import RepositoryImportGraph


@dataclass(frozen=True)
class RepositoryImportGraphSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryImportGraphSummaryBuilder:
    def build(self, graph: RepositoryImportGraph) -> RepositoryImportGraphSummary:
        if graph.edge_count == 0:
            return RepositoryImportGraphSummary(
                outcome="no_imports",
                message="Repository import graph found no Python import edges.",
                action_required=False,
            )

        return RepositoryImportGraphSummary(
            outcome="imports_detected",
            message=(
                f"Repository import graph found {graph.edge_count} import edge(s) "
                f"across {graph.source_file_count} source file(s)."
            ),
            action_required=False,
        )
