from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.code_intelligence_report import CodeIntelligenceReport


@dataclass(frozen=True)
class CodeIntelligenceOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class CodeIntelligenceSummaryBuilder:
    def build(self, report: CodeIntelligenceReport) -> CodeIntelligenceOperatorSummary:
        if not report.has_inventory:
            return CodeIntelligenceOperatorSummary(
                outcome="no_inventory",
                message="Code intelligence found no supported repository files.",
                action_required=False,
            )

        if not report.has_outline:
            return CodeIntelligenceOperatorSummary(
                outcome="inventory_without_symbols",
                message=(
                    f"Code intelligence inventoried {report.file_count} file(s) "
                    "but found no source symbols."
                ),
                action_required=False,
            )

        return CodeIntelligenceOperatorSummary(
            outcome="ready",
            message=(
                f"Code intelligence found {report.file_count} file(s), "
                f"{report.language_count} language(s), and {report.symbol_count} symbol(s)."
            ),
            action_required=False,
        )
