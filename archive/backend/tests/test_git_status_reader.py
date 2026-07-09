from app.connectors.repository import GitCommandResult, GitStatusReader, GitStatusReport, GitStatusEntry


class FakeRunner:
    def __init__(self, result):
        self.result = result

    def run(self, repository_path, args):
        self.repository_path = repository_path
        self.args = args
        return self.result


def test_git_status_report_clean_when_no_entries():
    report = GitStatusReport(entries=[])

    assert report.is_clean is True
    assert report.modified_count == 0
    assert report.untracked_count == 0


def test_git_status_report_counts_modified_and_untracked_entries():
    report = GitStatusReport(
        entries=[
            GitStatusEntry(status="M", path="README.md"),
            GitStatusEntry(status="??", path="new.md"),
        ]
    )

    assert report.is_clean is False
    assert report.modified_count == 1
    assert report.untracked_count == 1


def test_git_status_reader_parses_short_status():
    runner = FakeRunner(
        GitCommandResult(
            command=["git", "status", "--short"],
            cwd="/repo",
            returncode=0,
            stdout=" M README.md\n?? new.md\n",
            stderr="",
        )
    )

    report = GitStatusReader(runner).status("/repo")

    assert [entry.status for entry in report.entries] == ["M", "??"]
    assert [entry.path for entry in report.entries] == ["README.md", "new.md"]


def test_git_status_reader_raises_on_git_failure():
    runner = FakeRunner(
        GitCommandResult(
            command=["git", "status", "--short"],
            cwd="/repo",
            returncode=1,
            stdout="",
            stderr="fatal",
        )
    )

    try:
        GitStatusReader(runner).status("/repo")
    except RuntimeError as exc:
        assert "fatal" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")
