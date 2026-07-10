from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RepositoryImportEdge:
    source_file: str
    imported_name: str
    import_type: str
    line_number: int


@dataclass(frozen=True)
class RepositoryImportGraph:
    repository_path: str
    edges: list[RepositoryImportEdge] = field(default_factory=list)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def source_file_count(self) -> int:
        return len(self.source_files)

    @property
    def imported_name_count(self) -> int:
        return len(self.imported_names)

    @property
    def source_files(self) -> list[str]:
        return sorted({edge.source_file for edge in self.edges})

    @property
    def imported_names(self) -> list[str]:
        return sorted({edge.imported_name for edge in self.edges})

    def edges_for_source(self, source_file: str) -> list[RepositoryImportEdge]:
        return [edge for edge in self.edges if edge.source_file == source_file]


class RepositoryImportGraphBuilder:
    ignored_names = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}

    def build(self, repository_path: str | Path, max_depth: int = 8) -> RepositoryImportGraph:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")

        edges: list[RepositoryImportEdge] = []

        for path in sorted(root.rglob("*.py")):
            relative = path.relative_to(root)
            parts = relative.parts

            if any(part in self.ignored_names for part in parts):
                continue

            if len(parts) > max_depth:
                continue

            edges.extend(self._parse_python_imports(path, relative.as_posix()))

        return RepositoryImportGraph(repository_path=str(root), edges=edges)

    def _parse_python_imports(self, path: Path, relative_path: str) -> list[RepositoryImportEdge]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            return []

        edges: list[RepositoryImportEdge] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    edges.append(
                        RepositoryImportEdge(
                            source_file=relative_path,
                            imported_name=alias.name,
                            import_type="import",
                            line_number=node.lineno,
                        )
                    )

            if isinstance(node, ast.ImportFrom):
                module = "." * node.level + (node.module or "")
                for alias in node.names:
                    imported = f"{module}.{alias.name}" if module else alias.name
                    edges.append(
                        RepositoryImportEdge(
                            source_file=relative_path,
                            imported_name=imported,
                            import_type="from_import",
                            line_number=node.lineno,
                        )
                    )

        return edges
