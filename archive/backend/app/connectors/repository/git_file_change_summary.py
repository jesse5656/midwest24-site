from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.git_file_change import GitFileChangePreview


@dataclass(frozen=True)
class GitFileChangeOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class GitFileChangeSummaryBuilder:
    def build(self, preview: GitFileChangePreview) -> GitFileChangeOperatorSummary:
        if preview.commit_count == 0:
            return GitFileChangeOperatorSummary(
                outcome="no_file_changes",
                message="No Git file changes were found in the requested preview.",
                action_required=False,
            )

        if preview.file_change_count == 0:
            return GitFileChangeOperatorSummary(
                outcome="commits_without_file_changes",
                message=f"{preview.commit_count} commit(s) were found without file-change entries.",
                action_required=False,
            )

        return GitFileChangeOperatorSummary(
            outcome="file_changes_found",
            message=(
                f"Git file-change preview found {preview.file_change_count} file change(s) "
                f"across {preview.commit_count} commit(s)."
            ),
            action_required=False,
        )
