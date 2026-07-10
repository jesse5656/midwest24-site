from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_summary import RepositorySummary


@dataclass(frozen=True)
class RepositorySummarySummary:
    outcome: str
    message: str
    action_required: bool


class RepositorySummarySummaryBuilder:
    def build(self, summary: RepositorySummary) -> RepositorySummarySummary:
        if summary.section_count == 0:
            return RepositorySummarySummary(
                outcome="empty_summary",
                message="Repository summary has no sections.",
                action_required=True,
            )

        return RepositorySummarySummary(
            outcome="summary_built",
            message=f"{summary.title} built with {summary.section_count} section(s).",
            action_required=False,
        )
