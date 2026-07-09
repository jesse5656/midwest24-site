from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.git_preview import GitCommitPreview


@dataclass(frozen=True)
class GitCommitPreviewOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class GitCommitPreviewSummaryBuilder:
    def build(self, preview: GitCommitPreview) -> GitCommitPreviewOperatorSummary:
        if preview.commit_count == 0:
            return GitCommitPreviewOperatorSummary(
                outcome="no_commits",
                message="No commits were found in the requested Git history preview.",
                action_required=False,
            )

        if len(preview.authors) > 1:
            return GitCommitPreviewOperatorSummary(
                outcome="multi_author_history",
                message=(
                    f"Git history preview includes {preview.commit_count} commit(s) "
                    f"from {len(preview.authors)} author(s)."
                ),
                action_required=False,
            )

        return GitCommitPreviewOperatorSummary(
            outcome="single_author_history",
            message=f"Git history preview includes {preview.commit_count} commit(s) from one author.",
            action_required=False,
        )
