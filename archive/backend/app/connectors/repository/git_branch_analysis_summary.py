from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.git_branch_analysis import GitBranchAnalysis


@dataclass(frozen=True)
class GitBranchAnalysisOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class GitBranchAnalysisSummaryBuilder:
    def build(self, analysis: GitBranchAnalysis) -> GitBranchAnalysisOperatorSummary:
        if analysis.branch_count == 0:
            return GitBranchAnalysisOperatorSummary(
                outcome="no_branches",
                message="No Git branches were found.",
                action_required=False,
            )

        if analysis.current_branch_name is None:
            return GitBranchAnalysisOperatorSummary(
                outcome="no_current_branch",
                message=f"{analysis.branch_count} branch(es) were found, but no current branch was detected.",
                action_required=False,
            )

        if analysis.has_multiple_branches:
            return GitBranchAnalysisOperatorSummary(
                outcome="multiple_branches",
                message=(
                    f"Git branch analysis found {analysis.branch_count} branch(es); "
                    f"current branch is {analysis.current_branch_name}."
                ),
                action_required=False,
            )

        return GitBranchAnalysisOperatorSummary(
            outcome="single_branch",
            message=f"Git branch analysis found one branch: {analysis.current_branch_name}.",
            action_required=False,
        )
