import pytest

from app.connectors.repository import GitCommandResult, GitHistoryReader


class FakeRunner:
    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr
        self.args = None

    def run(self, repository_path, args):
        self.args = args
        return GitCommandResult(
            command=["git", *args],
            cwd=str(repository_path),
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
        )


def test_git_history_reader_reads_recent_commits():
    runner = FakeRunner(
        stdout="abcdef\x1fabc\x1fJesse\x1fjesse@example.com\x1f2026-01-01T00:00:00Z\x1fSubject"
    )

    commits = GitHistoryReader(runner=runner).recent_commits("/repo", limit=3)

    assert len(commits) == 1
    assert commits[0].subject == "Subject"
    assert "--max-count=3" in runner.args


def test_git_history_reader_rejects_zero_limit():
    with pytest.raises(ValueError):
        GitHistoryReader(runner=FakeRunner()).recent_commits("/repo", limit=0)


def test_git_history_reader_raises_on_git_failure():
    runner = FakeRunner(returncode=1, stderr="fatal log error")

    with pytest.raises(RuntimeError) as exc:
        GitHistoryReader(runner=runner).recent_commits("/repo")

    assert "fatal log error" in str(exc.value)
