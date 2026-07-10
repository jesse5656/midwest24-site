from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_cross_reference_graph import RepositoryCrossReferenceGraph


@dataclass(frozen=True)
class RepositoryCrossReferenceGraphSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryCrossReferenceGraphSummaryBuilder:
    def build(self, graph: RepositoryCrossReferenceGraph) -> RepositoryCrossReferenceGraphSummary:
        if graph.reference_count == 0:
            return RepositoryCrossReferenceGraphSummary(
                outcome="no_references",
                message="Repository cross-reference graph found no Python references.",
                action_required=False,
            )

        return RepositoryCrossReferenceGraphSummary(
            outcome="references_detected",
            message=(
                f"Repository cross-reference graph found {graph.reference_count} reference(s) "
                f"across {graph.source_file_count} source file(s): "
                f"{graph.call_count} call(s), "
                f"{graph.attribute_count} attribute reference(s), "
                f"{graph.name_count} name reference(s)."
            ),
            action_required=False,
        )
