from app.connectors.repository import GitBranch, GitBranchAnalysisBuilder


class FakeBranchReader:
    def __init__(self, branches):
        self.branches_value = branches
        self.repository_path = None

    def branches(self, repository_path):
        self.repository_path = repository_path
        return self.branches_value


def test_branch_analysis_builder_uses_branch_reader():
    reader = FakeBranchReader([GitBranch(name="main", current=True)])

    analysis = GitBranchAnalysisBuilder(branch_reader=reader).build("/repo")

    assert analysis.branch_count == 1
    assert analysis.current_branch_name == "main"
    assert reader.repository_path == "/repo"


def test_branch_analysis_builder_handles_empty_branch_list():
    reader = FakeBranchReader([])

    analysis = GitBranchAnalysisBuilder(branch_reader=reader).build("/repo")

    assert analysis.branch_count == 0
    assert analysis.current_branch is None
