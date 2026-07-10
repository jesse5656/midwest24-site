from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_symbol_index import RepositorySymbolIndex


@dataclass(frozen=True)
class RepositorySymbolIndexSummary:
    outcome: str
    message: str
    action_required: bool


class RepositorySymbolIndexSummaryBuilder:
    def build(self, index: RepositorySymbolIndex) -> RepositorySymbolIndexSummary:
        if index.symbol_count == 0:
            return RepositorySymbolIndexSummary(
                outcome="no_symbols",
                message="Repository symbol index found no Python symbols.",
                action_required=False,
            )

        return RepositorySymbolIndexSummary(
            outcome="symbols_detected",
            message=(
                f"Repository symbol index found {index.symbol_count} symbol(s) "
                f"across {index.source_file_count} source file(s): "
                f"{index.class_count} class(es), "
                f"{index.function_count} function(s), "
                f"{index.method_count} method(s), "
                f"{index.constant_count} constant(s)."
            ),
            action_required=False,
        )
