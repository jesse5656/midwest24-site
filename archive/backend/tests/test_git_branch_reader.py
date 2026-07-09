from app.connectors.repository import GitBranchReader, GitCommandResult


class FakeRunner:
    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr

    def run(self, repository_path, args):
        return GitCommandResult(
            command=["git", *args],
            cwd=str(repository_path),
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
        )


def test_git_branch_reader_parses_current_branch():
    reader = GitBranchReader(
        FakeRunner(stdout="*\x1fmain\n \x1ffeature\n")
    )

    branches = reader.branches("/repo")

    assert [branch.name for branch in branches] == ["main", "feature"]
    assert branches[0].current is True
    assert branches[1].current is False


def test_git_branch_reader_returns_current_branch():
    reader = GitBranchReader(
        FakeRunner(stdout=" \x1fdev\n*\x1fmain\n")
    )

    branch = reader.current_branch("/repo")

    assert branch.name == "main"
    assert branch.current is True


def test_git_branch_reader_returns_none_without_current_branch():
    reader = GitBranchReader(
        FakeRunner(stdout=" \x1fdev\n \x1fmain\n")
    )

    assert reader.current_branch("/repo") is None


def test_git_branch_reader_raises_on_git_failure():
    reader = GitBranchReader(
        FakeRunner(returncode=1, stderr="fatal branch error")
    )

    try:
        reader.branches("/repo")
    except RuntimeError as exc:
        assert "fatal branch error" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")
