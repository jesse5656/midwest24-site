from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RepositorySymbol:
    name: str
    symbol_type: str
    source_file: str
    line_number: int
    parent: str | None = None

    @property
    def qualified_name(self) -> str:
        if self.parent:
            return f"{self.parent}.{self.name}"
        return self.name


@dataclass(frozen=True)
class RepositorySymbolIndex:
    repository_path: str
    symbols: list[RepositorySymbol] = field(default_factory=list)

    @property
    def symbol_count(self) -> int:
        return len(self.symbols)

    @property
    def source_file_count(self) -> int:
        return len(self.source_files)

    @property
    def source_files(self) -> list[str]:
        return sorted({symbol.source_file for symbol in self.symbols})

    @property
    def symbol_types(self) -> list[str]:
        return sorted({symbol.symbol_type for symbol in self.symbols})

    @property
    def class_count(self) -> int:
        return sum(1 for symbol in self.symbols if symbol.symbol_type == "class")

    @property
    def function_count(self) -> int:
        return sum(1 for symbol in self.symbols if symbol.symbol_type == "function")

    @property
    def method_count(self) -> int:
        return sum(1 for symbol in self.symbols if symbol.symbol_type == "method")

    @property
    def constant_count(self) -> int:
        return sum(1 for symbol in self.symbols if symbol.symbol_type == "constant")

    def symbols_for_file(self, source_file: str) -> list[RepositorySymbol]:
        return [symbol for symbol in self.symbols if symbol.source_file == source_file]

    def symbols_by_type(self, symbol_type: str) -> list[RepositorySymbol]:
        return [symbol for symbol in self.symbols if symbol.symbol_type == symbol_type]


class RepositorySymbolIndexBuilder:
    ignored_names = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}

    def build(self, repository_path: str | Path, max_depth: int = 8) -> RepositorySymbolIndex:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")

        symbols: list[RepositorySymbol] = []

        for path in sorted(root.rglob("*.py")):
            relative = path.relative_to(root)
            parts = relative.parts

            if any(part in self.ignored_names for part in parts):
                continue

            if len(parts) > max_depth:
                continue

            symbols.extend(self._parse_python_symbols(path, relative.as_posix()))

        return RepositorySymbolIndex(repository_path=str(root), symbols=symbols)

    def _parse_python_symbols(self, path: Path, relative_path: str) -> list[RepositorySymbol]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            return []

        symbols: list[RepositorySymbol] = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                symbols.append(
                    RepositorySymbol(
                        name=node.name,
                        symbol_type="class",
                        source_file=relative_path,
                        line_number=node.lineno,
                    )
                )

                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        symbols.append(
                            RepositorySymbol(
                                name=child.name,
                                symbol_type="method",
                                source_file=relative_path,
                                line_number=child.lineno,
                                parent=node.name,
                            )
                        )

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append(
                    RepositorySymbol(
                        name=node.name,
                        symbol_type="function",
                        source_file=relative_path,
                        line_number=node.lineno,
                    )
                )

            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        symbols.append(
                            RepositorySymbol(
                                name=target.id,
                                symbol_type="constant",
                                source_file=relative_path,
                                line_number=node.lineno,
                            )
                        )

            elif isinstance(node, ast.AnnAssign):
                target = node.target
                if isinstance(target, ast.Name) and target.id.isupper():
                    symbols.append(
                        RepositorySymbol(
                            name=target.id,
                            symbol_type="constant",
                            source_file=relative_path,
                            line_number=node.lineno,
                        )
                    )

        return symbols
