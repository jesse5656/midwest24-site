from app.api.git_branch_analysis import serialize_git_branch, serialize_git_branch_analysis
from app.connectors.repository import GitBranch, GitBranchAnalysis


def test_serialize_git_branch_returns_none_for_none():
    assert serialize_git_branch(None) is None


def test_serialize_git_branch_maps_fields():
    response = serialize_git_branch(GitBranch(name="main", current=True))

    assert response.name == "main"
    assert response.current is True


def test_serialize_git_branch_analysis_maps_counts_and_names():
    analysis = GitBranchAnalysis(
        branches=[
            GitBranch(name="main", current=True),
            GitBranch(name="dev"),
        ]
    )

    response = serialize_git_branch_analysis(analysis)

    assert response.branch_count == 2
    assert response.current_branch_name == "main"
    assert response.branch_names == ["main", "dev"]
    assert response.non_current_branch_names == ["dev"]


def test_serialize_git_branch_analysis_maps_summary():
    response = serialize_git_branch_analysis(
        GitBranchAnalysis(branches=[GitBranch(name="main", current=True)])
    )

    assert response.summary.outcome == "single_branch"


def test_serialize_git_branch_analysis_maps_no_current_branch():
    response = serialize_git_branch_analysis(GitBranchAnalysis(branches=[GitBranch(name="dev")]))

    assert response.current_branch is None
    assert response.summary.outcome == "no_current_branch"
