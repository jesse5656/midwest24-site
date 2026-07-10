from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RepositoryStructureNode:
    path: str
    node_type: str
    depth: int
    child_count: int = 0


@dataclass(frozen=True)
class RepositoryStructureReport:
    repository_path: str
    nodes: list[RepositoryStructureNode] = field(default_factory=list)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def file_count(self) -> int:
        return sum(1 for node in self.nodes if node.node_type == "file")

    @property
    def directory_count(self) -> int:
        return sum(1 for node in self.nodes if node.node_type == "directory")

    @property
    def max_depth(self) -> int:
        if not self.nodes:
            return 0
        return max(node.depth for node in self.nodes)

    @property
    def top_level_nodes(self) -> list[RepositoryStructureNode]:
        return [node for node in self.nodes if node.depth == 1]


class RepositoryStructureBuilder:
    ignored_names = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}

    def build(self, repository_path: str | Path, max_depth: int = 4) -> RepositoryStructureReport:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")

        nodes: list[RepositoryStructureNode] = []

        for path in sorted(root.rglob("*")):
            relative = path.relative_to(root)
            parts = relative.parts

            if any(part in self.ignored_names for part in parts):
                continue

            depth = len(parts)

            if depth > max_depth:
                continue

            if path.is_dir():
                children = [
                    child for child in path.iterdir()
                    if child.name not in self.ignored_names
                ]
                nodes.append(
                    RepositoryStructureNode(
                        path=relative.as_posix(),
                        node_type="directory",
                        depth=depth,
                        child_count=len(children),
                    )
                )
            elif path.is_file():
                nodes.append(
                    RepositoryStructureNode(
                        path=relative.as_posix(),
                        node_type="file",
                        depth=depth,
                        child_count=0,
                    )
                )

        return RepositoryStructureReport(
            repository_path=str(root),
            nodes=nodes,
        )
