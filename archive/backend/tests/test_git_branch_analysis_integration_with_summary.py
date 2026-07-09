from app.connectors.repository import GitBranch, GitBranchAnalysis, GitBranchAnalysisSummaryBuilder


def test_branch_analysis_multi_branch_summary_uses_current_branch_name():
    analysis = GitBranchAnalysis(
        branches=[
            GitBranch(name="release", current=True),
            GitBranch(name="main"),
            GitBranch(name="dev"),
        ]
    )

    summary = GitBranchAnalysisSummaryBuilder().build(analysis)

    assert summary.outcome == "multiple_branches"
    assert "release" in summary.message


def test_branch_analysis_no_branch_summary_handles_empty_names():
    analysis = GitBranchAnalysis()

    summary = GitBranchAnalysisSummaryBuilder().build(analysis)

    assert analysis.branch_names == []
    assert summary.outcome == "no_branches"


def test_branch_analysis_non_current_list_excludes_current_branch():
    analysis = GitBranchAnalysis(
        branches=[
            GitBranch(name="main", current=True),
            GitBranch(name="feature"),
        ]
    )

    assert "main" not in analysis.non_current_branch_names
    assert "feature" in analysis.non_current_branch_names


def test_branch_analysis_current_branch_is_first_current_if_multiple_marked():
    first = GitBranch(name="main", current=True)
    second = GitBranch(name="dev", current=True)

    analysis = GitBranchAnalysis(branches=[first, second])

    assert analysis.current_branch == first
