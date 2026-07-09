from pathlib import Path

from app.connectors.repository import GitCommandResult, GitRepositoryDetector


class FakeRunner:
    def __init__(self, responses):
        self.responses = responses

    def run(self, repository_path, args):
        key = tuple(args)
        return self.responses[key]


def result(stdout="", returncode=0, stderr=""):
    return GitCommandResult(
        command=["git"],
        cwd="/repo",
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_git_repository_detector_returns_false_for_missing_path(tmp_path: Path):
    detector = GitRepositoryDetector(FakeRunner({}))

    assert detector.is_git_repository(tmp_path / "missing") is False


def test_git_repository_detector_returns_true_for_git_work_tree(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    detector = GitRepositoryDetector(
        FakeRunner({("rev-parse", "--is-inside-work-tree"): result(stdout="true\n")})
    )

    assert detector.is_git_repository(repo) is True


def test_git_repository_detector_returns_false_for_non_git_directory(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    detector = GitRepositoryDetector(
        FakeRunner({("rev-parse", "--is-inside-work-tree"): result(stdout="false\n", returncode=1)})
    )

    assert detector.is_git_repository(repo) is False


def test_git_repository_detector_returns_repository_root(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    detector = GitRepositoryDetector(
        FakeRunner({("rev-parse", "--show-toplevel"): result(stdout=str(repo) + "\n")})
    )

    assert detector.repository_root(repo) == repo.resolve()


def test_git_repository_detector_returns_current_branch(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    detector = GitRepositoryDetector(
        FakeRunner({("branch", "--show-current"): result(stdout="main\n")})
    )

    assert detector.current_branch(repo) == "main"


def test_git_repository_detector_returns_none_for_empty_current_branch(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    detector = GitRepositoryDetector(
        FakeRunner({("branch", "--show-current"): result(stdout="\n")})
    )

    assert detector.current_branch(repo) is None
