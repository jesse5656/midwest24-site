from app.connectors.repository import GitBranch, GitBranchAnalysis, GitBranchAnalysisSummaryBuilder


def test_branch_analysis_summary_reports_no_branches():
    summary = GitBranchAnalysisSummaryBuilder().build(GitBranchAnalysis())

    assert summary.outcome == "no_branches"
    assert summary.action_required is False


def test_branch_analysis_summary_reports_no_current_branch():
    analysis = GitBranchAnalysis(branches=[GitBranch(name="dev")])

    summary = GitBranchAnalysisSummaryBuilder().build(analysis)

    assert summary.outcome == "no_current_branch"
    assert "no current branch" in summary.message


def test_branch_analysis_summary_reports_multiple_branches():
    analysis = GitBranchAnalysis(
        branches=[
            GitBranch(name="main", current=True),
            GitBranch(name="dev"),
        ]
    )

    summary = GitBranchAnalysisSummaryBuilder().build(analysis)

    assert summary.outcome == "multiple_branches"
    assert "2 branch" in summary.message
    assert "main" in summary.message


def test_branch_analysis_summary_reports_single_branch():
    analysis = GitBranchAnalysis(branches=[GitBranch(name="main", current=True)])

    summary = GitBranchAnalysisSummaryBuilder().build(analysis)

    assert summary.outcome == "single_branch"
    assert "main" in summary.message


def test_branch_analysis_summary_never_requires_action():
    summaries = [
        GitBranchAnalysisSummaryBuilder().build(GitBranchAnalysis()),
        GitBranchAnalysisSummaryBuilder().build(GitBranchAnalysis(branches=[GitBranch(name="dev")])),
        GitBranchAnalysisSummaryBuilder().build(GitBranchAnalysis(branches=[GitBranch(name="main", current=True)])),
    ]

    assert all(summary.action_required is False for summary in summaries)
