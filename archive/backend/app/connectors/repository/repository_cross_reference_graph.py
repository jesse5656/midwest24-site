from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RepositoryCrossReference:
    source_file: str
    source_symbol: str | None
    referenced_name: str
    reference_type: str
    line_number: int


@dataclass(frozen=True)
class RepositoryCrossReferenceGraph:
    repository_path: str
    references: list[RepositoryCrossReference] = field(default_factory=list)

    @property
    def reference_count(self) -> int:
        return len(self.references)

    @property
    def source_file_count(self) -> int:
        return len(self.source_files)

    @property
    def referenced_name_count(self) -> int:
        return len(self.referenced_names)

    @property
    def source_files(self) -> list[str]:
        return sorted({reference.source_file for reference in self.references})

    @property
    def referenced_names(self) -> list[str]:
        return sorted({reference.referenced_name for reference in self.references})

    @property
    def call_count(self) -> int:
        return sum(1 for reference in self.references if reference.reference_type == "call")

    @property
    def attribute_count(self) -> int:
        return sum(1 for reference in self.references if reference.reference_type == "attribute")

    @property
    def name_count(self) -> int:
        return sum(1 for reference in self.references if reference.reference_type == "name")

    def references_for_file(self, source_file: str) -> list[RepositoryCrossReference]:
        return [reference for reference in self.references if reference.source_file == source_file]

    def references_to_name(self, referenced_name: str) -> list[RepositoryCrossReference]:
        return [reference for reference in self.references if reference.referenced_name == referenced_name]


class RepositoryCrossReferenceGraphBuilder:
    ignored_names = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}

    def build(self, repository_path: str | Path, max_depth: int = 8) -> RepositoryCrossReferenceGraph:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")

        references: list[RepositoryCrossReference] = []

        for path in sorted(root.rglob("*.py")):
            relative = path.relative_to(root)
            parts = relative.parts

            if any(part in self.ignored_names for part in parts):
                continue

            if len(parts) > max_depth:
                continue

            references.extend(self._parse_python_references(path, relative.as_posix()))

        return RepositoryCrossReferenceGraph(repository_path=str(root), references=references)

    def _parse_python_references(self, path: Path, relative_path: str) -> list[RepositoryCrossReference]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            return []

        visitor = _ReferenceVisitor(relative_path)
        visitor.visit(tree)
        return visitor.references


class _ReferenceVisitor(ast.NodeVisitor):
    def __init__(self, source_file: str):
        self.source_file = source_file
        self.symbol_stack: list[str] = []
        self.references: list[RepositoryCrossReference] = []

    @property
    def current_symbol(self) -> str | None:
        if not self.symbol_stack:
            return None
        return ".".join(self.symbol_stack)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.symbol_stack.append(node.name)
        self.generic_visit(node)
        self.symbol_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.symbol_stack.append(node.name)
        self.generic_visit(node)
        self.symbol_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.symbol_stack.append(node.name)
        self.generic_visit(node)
        self.symbol_stack.pop()

    def visit_Call(self, node: ast.Call):
        name = self._name_for_expression(node.func)
        if name:
            self.references.append(
                RepositoryCrossReference(
                    source_file=self.source_file,
                    source_symbol=self.current_symbol,
                    referenced_name=name,
                    reference_type="call",
                    line_number=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        name = self._name_for_expression(node)
        if name:
            self.references.append(
                RepositoryCrossReference(
                    source_file=self.source_file,
                    source_symbol=self.current_symbol,
                    referenced_name=name,
                    reference_type="attribute",
                    line_number=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load):
            self.references.append(
                RepositoryCrossReference(
                    source_file=self.source_file,
                    source_symbol=self.current_symbol,
                    referenced_name=node.id,
                    reference_type="name",
                    line_number=node.lineno,
                )
            )
        self.generic_visit(node)

    def _name_for_expression(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            parent = self._name_for_expression(node.value)
            if parent:
                return f"{parent}.{node.attr}"
            return node.attr

        return None
