from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_semantic_search import (
    RepositorySemanticSearchReport,
)


@dataclass(frozen=True)
class RepositorySemanticSearchSummary:
    outcome: str
    message: str
    action_required: bool


class RepositorySemanticSearchSummaryBuilder:
    def build(
        self,
        report: RepositorySemanticSearchReport,
    ) -> RepositorySemanticSearchSummary:
        if not report.query.strip():
            return RepositorySemanticSearchSummary(
                outcome="empty_query",
                message="Repository semantic search requires a non-empty query.",
                action_required=True,
            )

        if report.result_count == 0:
            return RepositorySemanticSearchSummary(
                outcome="no_results",
                message=(
                    f'Repository semantic search found no results for '
                    f'"{report.query}".'
                ),
                action_required=False,
            )

        return RepositorySemanticSearchSummary(
            outcome="results_found",
            message=(
                f'Repository semantic search found {report.result_count} '
                f'result(s) for "{report.query}" with highest score '
                f"{report.highest_score}."
            ),
            action_required=False,
        )
