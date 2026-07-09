from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.code_inventory import LANGUAGE_BY_SUFFIX
from app.connectors.repository.filesystem_repository_connector import RepositoryFilesystemConnector


@dataclass(frozen=True)
class SourceOutlineSymbol:
    name: str
    symbol_type: str
    line_number: int


@dataclass(frozen=True)
class SourceOutlineFile:
    path: str
    suffix: str
    language: str
    symbols: list[SourceOutlineSymbol] = field(default_factory=list)

    @property
    def symbol_count(self) -> int:
        return len(self.symbols)

    @property
    def function_count(self) -> int:
        return sum(1 for symbol in self.symbols if symbol.symbol_type == "function")

    @property
    def class_count(self) -> int:
        return sum(1 for symbol in self.symbols if symbol.symbol_type == "class")


@dataclass(frozen=True)
class SourceOutlinePreview:
    files: list[SourceOutlineFile] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def symbol_count(self) -> int:
        return sum(file.symbol_count for file in self.files)

    @property
    def function_count(self) -> int:
        return sum(file.function_count for file in self.files)

    @property
    def class_count(self) -> int:
        return sum(file.class_count for file in self.files)

    @property
    def files_with_symbols(self) -> list[SourceOutlineFile]:
        return [file for file in self.files if file.symbol_count > 0]


class SourceOutlineParser:
    PY_FUNCTION = re.compile(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    PY_CLASS = re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\s*[\(:]")
    JS_FUNCTION = re.compile(r"^\s*(?:export\s+)?function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(")
    JS_CLASS = re.compile(r"^\s*(?:export\s+)?class\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*")
    JS_CONST_FUNCTION = re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?\(")

    def parse(self, path: str, suffix: str, text: str) -> SourceOutlineFile:
        language = LANGUAGE_BY_SUFFIX.get(suffix, "Unknown")
        symbols: list[SourceOutlineSymbol] = []

        for index, line in enumerate(text.splitlines(), start=1):
            symbol = self._parse_line(suffix, line, index)
            if symbol is not None:
                symbols.append(symbol)

        return SourceOutlineFile(
            path=path,
            suffix=suffix,
            language=language,
            symbols=symbols,
        )

    def _parse_line(self, suffix: str, line: str, line_number: int):
        if suffix == ".py":
            function = self.PY_FUNCTION.match(line)
            if function:
                return SourceOutlineSymbol(function.group(1), "function", line_number)

            cls = self.PY_CLASS.match(line)
            if cls:
                return SourceOutlineSymbol(cls.group(1), "class", line_number)

        if suffix in {".js", ".jsx", ".ts", ".tsx"}:
            function = self.JS_FUNCTION.match(line)
            if function:
                return SourceOutlineSymbol(function.group(1), "function", line_number)

            const_function = self.JS_CONST_FUNCTION.match(line)
            if const_function:
                return SourceOutlineSymbol(const_function.group(1), "function", line_number)

            cls = self.JS_CLASS.match(line)
            if cls:
                return SourceOutlineSymbol(cls.group(1), "class", line_number)

        return None


class SourceOutlinePreviewBuilder:
    def __init__(self, parser: SourceOutlineParser | None = None):
        self.parser = parser or SourceOutlineParser()

    def build(self, repository_path: str | Path) -> SourceOutlinePreview:
        connector = RepositoryFilesystemConnector(repository_path)
        repository_files = connector.discover()

        outline_files = []

        for file in repository_files:
            if file.suffix not in {".py", ".js", ".jsx", ".ts", ".tsx"}:
                continue

            text = file.path.read_text(errors="ignore")

            outline_files.append(
                self.parser.parse(
                    path=file.relative_path,
                    suffix=file.suffix,
                    text=text,
                )
            )

        return SourceOutlinePreview(files=outline_files)
