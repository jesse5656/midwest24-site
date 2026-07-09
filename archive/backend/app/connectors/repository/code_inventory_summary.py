from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.code_inventory import CodeInventoryPreview


@dataclass(frozen=True)
class CodeInventoryOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class CodeInventorySummaryBuilder:
    def build(self, preview: CodeInventoryPreview) -> CodeInventoryOperatorSummary:
        if preview.file_count == 0:
            return CodeInventoryOperatorSummary(
                outcome="empty_inventory",
                message="No supported files were found for code inventory.",
                action_required=False,
            )

        if preview.language_count == 1:
            return CodeInventoryOperatorSummary(
                outcome="single_language_inventory",
                message=f"Code inventory found {preview.file_count} file(s) in one language.",
                action_required=False,
            )

        return CodeInventoryOperatorSummary(
            outcome="multi_language_inventory",
            message=(
                f"Code inventory found {preview.file_count} file(s) "
                f"across {preview.language_count} language(s)."
            ),
            action_required=False,
        )
