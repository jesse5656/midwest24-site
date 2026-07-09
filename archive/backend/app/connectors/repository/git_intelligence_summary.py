from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.git_intelligence_report import GitIntelligenceReport


@dataclass(frozen=True)
class GitIntelligenceOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class GitIntelligenceSummaryBuilder:
    def build(self, report: GitIntelligenceReport) -> GitIntelligenceOperatorSummary:
        if not report.is_repository:
            return GitIntelligenceOperatorSummary(
                outcome="not_git_repository",
                message="Git intelligence could not run because the path is not a Git repository.",
                action_required=True,
            )

        if report.commit_count == 0:
            return GitIntelligenceOperatorSummary(
                outcome="no_commits",
                message="Git repository detected, but no commits were found.",
                action_required=False,
            )

        if report.has_uncommitted_changes:
            return GitIntelligenceOperatorSummary(
                outcome="repository_has_changes",
                message=(
                    f"Git repository intelligence found {report.commit_count} commit(s), "
                    f"{report.author_count} author(s), and uncommitted changes."
                ),
                action_required=False,
            )

        return GitIntelligenceOperatorSummary(
            outcome="ready",
            message=(
                f"Git repository intelligence is ready with {report.commit_count} commit(s), "
                f"{report.author_count} author(s), and {report.file_change_count} file change(s)."
            ),
            action_required=False,
        )
