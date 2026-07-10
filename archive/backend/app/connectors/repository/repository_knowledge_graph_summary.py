from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_knowledge_graph import RepositoryKnowledgeGraph


@dataclass(frozen=True)
class RepositoryKnowledgeGraphSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryKnowledgeGraphSummaryBuilder:
    def build(self, graph: RepositoryKnowledgeGraph) -> RepositoryKnowledgeGraphSummary:
        if graph.node_count == 0:
            return RepositoryKnowledgeGraphSummary(
                outcome="empty_graph",
                message="Repository knowledge graph has no nodes.",
                action_required=True,
            )

        return RepositoryKnowledgeGraphSummary(
            outcome="graph_built",
            message=(
                f"Repository knowledge graph built with {graph.node_count} node(s), "
                f"{graph.edge_count} edge(s), "
                f"{graph.file_node_count} file node(s), "
                f"{graph.dependency_node_count} dependency node(s), "
                f"{graph.import_node_count} import node(s), and "
                f"{graph.symbol_node_count} symbol node(s)."
            ),
            action_required=False,
        )
