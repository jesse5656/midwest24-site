from app.connectors.repository import GitBranch, GitBranchAnalysis


def test_branch_analysis_counts_branches():
    analysis = GitBranchAnalysis(
        branches=[
            GitBranch(name="main", current=True),
            GitBranch(name="dev", current=False),
        ]
    )

    assert analysis.branch_count == 2


def test_branch_analysis_returns_current_branch():
    current = GitBranch(name="main", current=True)
    analysis = GitBranchAnalysis(branches=[GitBranch(name="dev"), current])

    assert analysis.current_branch == current


def test_branch_analysis_current_branch_none_when_missing():
    analysis = GitBranchAnalysis(branches=[GitBranch(name="dev")])

    assert analysis.current_branch is None


def test_branch_analysis_current_branch_name():
    analysis = GitBranchAnalysis(branches=[GitBranch(name="main", current=True)])

    assert analysis.current_branch_name == "main"


def test_branch_analysis_current_branch_name_none_when_missing():
    analysis = GitBranchAnalysis(branches=[])

    assert analysis.current_branch_name is None


def test_branch_analysis_detects_multiple_branches():
    analysis = GitBranchAnalysis(
        branches=[
            GitBranch(name="main", current=True),
            GitBranch(name="dev"),
        ]
    )

    assert analysis.has_multiple_branches is True


def test_branch_analysis_single_branch_not_multiple():
    analysis = GitBranchAnalysis(branches=[GitBranch(name="main", current=True)])

    assert analysis.has_multiple_branches is False


def test_branch_analysis_branch_names_preserve_order():
    analysis = GitBranchAnalysis(
        branches=[
            GitBranch(name="main", current=True),
            GitBranch(name="dev"),
        ]
    )

    assert analysis.branch_names == ["main", "dev"]


def test_branch_analysis_non_current_branch_names():
    analysis = GitBranchAnalysis(
        branches=[
            GitBranch(name="main", current=True),
            GitBranch(name="dev"),
            GitBranch(name="feature"),
        ]
    )

    assert analysis.non_current_branch_names == ["dev", "feature"]


def test_branch_analysis_empty_branch_names():
    analysis = GitBranchAnalysis()

    assert analysis.branch_names == []
    assert analysis.non_current_branch_names == []
