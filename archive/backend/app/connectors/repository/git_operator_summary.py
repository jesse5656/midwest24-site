from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.git_summary import GitRepositorySummary


@dataclass(frozen=True)
class GitRepositoryOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class GitRepositoryOperatorSummaryBuilder:
    def build(self, summary: GitRepositorySummary) -> GitRepositoryOperatorSummary:
        if not summary.is_repository:
            return GitRepositoryOperatorSummary(
                outcome="not_git_repository",
                message="The supplied path is not a Git repository.",
                action_required=True,
            )

        if summary.current_branch is None:
            return GitRepositoryOperatorSummary(
                outcome="detached_or_unknown_branch",
                message="Git repository detected, but no current branch was reported.",
                action_required=False,
            )

        if summary.is_clean is False:
            return GitRepositoryOperatorSummary(
                outcome="repository_has_changes",
                message=(
                    f"Git repository detected on branch {summary.current_branch} "
                    "with uncommitted changes."
                ),
                action_required=False,
            )

        return GitRepositoryOperatorSummary(
            outcome="repository_clean",
            message=(
                f"Git repository detected on branch {summary.current_branch} "
                f"with {summary.recent_commit_count} recent commit(s)."
            ),
            action_required=False,
        )
