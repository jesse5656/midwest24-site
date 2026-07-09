from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.source_outline import SourceOutlinePreview


@dataclass(frozen=True)
class SourceOutlineOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class SourceOutlineSummaryBuilder:
    def build(self, preview: SourceOutlinePreview) -> SourceOutlineOperatorSummary:
        if preview.file_count == 0:
            return SourceOutlineOperatorSummary(
                outcome="no_source_files",
                message="No supported source files were found for outline preview.",
                action_required=False,
            )

        if preview.symbol_count == 0:
            return SourceOutlineOperatorSummary(
                outcome="no_symbols",
                message=f"Source outline scanned {preview.file_count} file(s) but found no symbols.",
                action_required=False,
            )

        return SourceOutlineOperatorSummary(
            outcome="symbols_found",
            message=(
                f"Source outline found {preview.symbol_count} symbol(s) "
                f"across {len(preview.files_with_symbols)} file(s)."
            ),
            action_required=False,
        )
