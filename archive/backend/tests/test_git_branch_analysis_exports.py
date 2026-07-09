from app.connectors.repository import (
    GitBranchAnalysis,
    GitBranchAnalysisBuilder,
    GitBranchAnalysisOperatorSummary,
    GitBranchAnalysisSummaryBuilder,
)


def test_branch_analysis_exports_are_available():
    assert GitBranchAnalysis is not None
    assert GitBranchAnalysisBuilder is not None


def test_branch_analysis_summary_exports_are_available():
    assert GitBranchAnalysisOperatorSummary is not None
    assert GitBranchAnalysisSummaryBuilder is not None
