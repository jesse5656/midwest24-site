from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.connectors.repository.code_inventory import CodeInventoryPreview, CodeInventoryPreviewBuilder
from app.connectors.repository.source_outline import SourceOutlinePreview, SourceOutlinePreviewBuilder


@dataclass(frozen=True)
class CodeIntelligenceReport:
    inventory: CodeInventoryPreview
    outline: SourceOutlinePreview

    @property
    def file_count(self) -> int:
        return self.inventory.file_count

    @property
    def language_count(self) -> int:
        return self.inventory.language_count

    @property
    def symbol_count(self) -> int:
        return self.outline.symbol_count

    @property
    def function_count(self) -> int:
        return self.outline.function_count

    @property
    def class_count(self) -> int:
        return self.outline.class_count

    @property
    def files_with_symbols_count(self) -> int:
        return len(self.outline.files_with_symbols)

    @property
    def has_inventory(self) -> bool:
        return self.file_count > 0

    @property
    def has_outline(self) -> bool:
        return self.symbol_count > 0

    @property
    def is_ready(self) -> bool:
        return self.has_inventory and self.has_outline


class CodeIntelligenceReportBuilder:
    def __init__(
        self,
        inventory_builder: CodeInventoryPreviewBuilder | None = None,
        outline_builder: SourceOutlinePreviewBuilder | None = None,
    ):
        self.inventory_builder = inventory_builder or CodeInventoryPreviewBuilder()
        self.outline_builder = outline_builder or SourceOutlinePreviewBuilder()

    def build(self, repository_path: str | Path) -> CodeIntelligenceReport:
        return CodeIntelligenceReport(
            inventory=self.inventory_builder.build(repository_path),
            outline=self.outline_builder.build(repository_path),
        )
