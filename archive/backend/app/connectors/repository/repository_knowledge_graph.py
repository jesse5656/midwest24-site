from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_dependency_map import RepositoryDependencyMapBuilder
from app.connectors.repository.repository_import_graph import RepositoryImportGraphBuilder
from app.connectors.repository.repository_package_map import RepositoryPackageMapBuilder
from app.connectors.repository.repository_structure import RepositoryStructureBuilder
from app.connectors.repository.repository_symbol_index import RepositorySymbolIndexBuilder


@dataclass(frozen=True)
class RepositoryKnowledgeGraphNode:
    node_id: str
    node_type: str
    label: str
    source: str


@dataclass(frozen=True)
class RepositoryKnowledgeGraphEdge:
    source_id: str
    target_id: str
    relationship: str


@dataclass(frozen=True)
class RepositoryKnowledgeGraph:
    repository_path: str
    nodes: list[RepositoryKnowledgeGraphNode] = field(default_factory=list)
    edges: list[RepositoryKnowledgeGraphEdge] = field(default_factory=list)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def node_types(self) -> list[str]:
        return sorted({node.node_type for node in self.nodes})

    @property
    def relationship_types(self) -> list[str]:
        return sorted({edge.relationship for edge in self.edges})

    @property
    def file_node_count(self) -> int:
        return sum(1 for node in self.nodes if node.node_type == "file")

    @property
    def package_node_count(self) -> int:
        return sum(1 for node in self.nodes if node.node_type == "package_marker")

    @property
    def dependency_node_count(self) -> int:
        return sum(1 for node in self.nodes if node.node_type == "dependency")

    @property
    def symbol_node_count(self) -> int:
        return sum(1 for node in self.nodes if node.node_type == "symbol")

    @property
    def import_node_count(self) -> int:
        return sum(1 for node in self.nodes if node.node_type == "import")

    def nodes_by_type(self, node_type: str) -> list[RepositoryKnowledgeGraphNode]:
        return [node for node in self.nodes if node.node_type == node_type]


class RepositoryKnowledgeGraphBuilder:
    def build(self, repository_path: str | Path, max_depth: int = 8) -> RepositoryKnowledgeGraph:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")

        structure = RepositoryStructureBuilder().build(root, max_depth=max_depth)
        package_map = RepositoryPackageMapBuilder().build(root, max_depth=max_depth)
        dependency_map = RepositoryDependencyMapBuilder().build(root, max_depth=max_depth)
        import_graph = RepositoryImportGraphBuilder().build(root, max_depth=max_depth)
        symbol_index = RepositorySymbolIndexBuilder().build(root, max_depth=max_depth)

        nodes_by_id: dict[str, RepositoryKnowledgeGraphNode] = {}
        edges: list[RepositoryKnowledgeGraphEdge] = []

        def add_node(node_id: str, node_type: str, label: str, source: str):
            nodes_by_id.setdefault(
                node_id,
                RepositoryKnowledgeGraphNode(
                    node_id=node_id,
                    node_type=node_type,
                    label=label,
                    source=source,
                ),
            )

        def add_edge(source_id: str, target_id: str, relationship: str):
            edge = RepositoryKnowledgeGraphEdge(
                source_id=source_id,
                target_id=target_id,
                relationship=relationship,
            )
            if edge not in edges:
                edges.append(edge)

        repository_id = "repository:root"
        add_node(repository_id, "repository", root.name, str(root))

        for node in structure.nodes:
            if node.node_type == "file":
                file_id = f"file:{node.path}"
                add_node(file_id, "file", node.path, node.path)
                add_edge(repository_id, file_id, "contains_file")

        for marker in package_map.markers:
            marker_id = f"package_marker:{marker.path}"
            add_node(marker_id, "package_marker", marker.marker_name, marker.path)
            add_edge(repository_id, marker_id, "has_package_marker")

        for dependency in dependency_map.dependencies:
            dependency_id = f"dependency:{dependency.ecosystem}:{dependency.name}"
            add_node(dependency_id, "dependency", dependency.name, dependency.source_file)
            add_edge(f"file:{dependency.source_file}", dependency_id, "declares_dependency")

        for import_edge in import_graph.edges:
            import_id = f"import:{import_edge.imported_name}"
            add_node(import_id, "import", import_edge.imported_name, import_edge.source_file)
            add_edge(f"file:{import_edge.source_file}", import_id, "imports")

        for symbol in symbol_index.symbols:
            symbol_id = f"symbol:{symbol.source_file}:{symbol.qualified_name}"
            add_node(symbol_id, "symbol", symbol.qualified_name, symbol.source_file)
            add_edge(f"file:{symbol.source_file}", symbol_id, "defines_symbol")

        return RepositoryKnowledgeGraph(
            repository_path=str(root),
            nodes=sorted(nodes_by_id.values(), key=lambda node: node.node_id),
            edges=sorted(edges, key=lambda edge: (edge.source_id, edge.target_id, edge.relationship)),
        )
