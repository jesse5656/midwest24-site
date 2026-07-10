from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_knowledge_graph import RepositoryKnowledgeGraphBuilder


@dataclass(frozen=True)
class RepositorySummarySection:
    name: str
    value: str


@dataclass(frozen=True)
class RepositorySummary:
    repository_path: str
    title: str
    sections: list[RepositorySummarySection] = field(default_factory=list)

    @property
    def section_count(self) -> int:
        return len(self.sections)

    @property
    def section_names(self) -> list[str]:
        return [section.name for section in self.sections]

    def section_value(self, name: str) -> str | None:
        for section in self.sections:
            if section.name == name:
                return section.value
        return None


class RepositorySummaryBuilder:
    def build(self, repository_path: str | Path, max_depth: int = 8) -> RepositorySummary:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")

        graph = RepositoryKnowledgeGraphBuilder().build(root, max_depth=max_depth)

        sections = [
            RepositorySummarySection("Repository", root.name),
            RepositorySummarySection("Files", str(graph.file_node_count)),
            RepositorySummarySection("Package Markers", str(graph.package_node_count)),
            RepositorySummarySection("Dependencies", str(graph.dependency_node_count)),
            RepositorySummarySection("Imports", str(graph.import_node_count)),
            RepositorySummarySection("Symbols", str(graph.symbol_node_count)),
            RepositorySummarySection("Knowledge Graph Nodes", str(graph.node_count)),
            RepositorySummarySection("Knowledge Graph Edges", str(graph.edge_count)),
        ]

        return RepositorySummary(
            repository_path=str(root),
            title=f"{root.name} Repository Summary",
            sections=sections,
        )
