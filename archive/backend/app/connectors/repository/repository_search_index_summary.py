from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_search_index import (
    RepositorySearchIndex,
)


@dataclass(frozen=True)
class RepositorySearchIndexSummary:
    outcome: str
    message: str
    action_required: bool


class RepositorySearchIndexSummaryBuilder:
    def build(
        self,
        index: RepositorySearchIndex,
    ) -> RepositorySearchIndexSummary:
        if index.document_count == 0:
            return RepositorySearchIndexSummary(
                outcome="empty_index",
                message="Repository search index has no documents.",
                action_required=True,
            )

        return RepositorySearchIndexSummary(
            outcome="index_built",
            message=(
                f"Repository search index built with "
                f"{index.document_count} document(s) across "
                f"{len(index.document_types)} document type(s)."
            ),
            action_required=False,
        )
