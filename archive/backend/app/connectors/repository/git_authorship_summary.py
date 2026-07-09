from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.git_authorship import GitAuthorshipPreview


@dataclass(frozen=True)
class GitAuthorshipOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class GitAuthorshipSummaryBuilder:
    def build(self, preview: GitAuthorshipPreview) -> GitAuthorshipOperatorSummary:
        if preview.commit_count == 0:
            return GitAuthorshipOperatorSummary(
                outcome="no_authorship",
                message="No Git authorship information was found in the requested preview.",
                action_required=False,
            )

        if preview.author_count == 1:
            top_author = preview.top_author
            return GitAuthorshipOperatorSummary(
                outcome="single_author",
                message=(
                    f"Git authorship preview includes {preview.commit_count} commit(s) "
                    f"from {top_author.identity}."
                ),
                action_required=False,
            )

        return GitAuthorshipOperatorSummary(
            outcome="multiple_authors",
            message=(
                f"Git authorship preview includes {preview.commit_count} commit(s) "
                f"from {preview.author_count} author(s)."
            ),
            action_required=False,
        )
