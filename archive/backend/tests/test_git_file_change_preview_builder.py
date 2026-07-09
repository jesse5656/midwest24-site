import pytest

from app.connectors.repository import GitCommandResult, GitFileChangePreviewBuilder


class FakeRunner:
    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr
        self.args = None
        self.repository_path = None

    def run(self, repository_path, args):
        self.repository_path = repository_path
        self.args = args
        return GitCommandResult(
            command=["git", *args],
            cwd=str(repository_path),
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
        )


def test_file_change_preview_builder_reads_git_log_name_status():
    runner = FakeRunner(stdout="\x1ea\x1fa\x1fA\nM\tREADME.md\n")

    preview = GitFileChangePreviewBuilder(runner=runner).build("/repo", limit=7)

    assert preview.commit_count == 1
    assert preview.file_change_count == 1
    assert "--max-count=7" in runner.args
    assert "--name-status" in runner.args


def test_file_change_preview_builder_rejects_zero_limit():
    with pytest.raises(ValueError):
        GitFileChangePreviewBuilder(runner=FakeRunner()).build("/repo", limit=0)


def test_file_change_preview_builder_raises_on_git_failure():
    runner = FakeRunner(returncode=1, stderr="fatal file changes")

    with pytest.raises(RuntimeError) as exc:
        GitFileChangePreviewBuilder(runner=runner).build("/repo")

    assert "fatal file changes" in str(exc.value)


def test_file_change_preview_builder_uses_default_error_message_when_stderr_empty():
    runner = FakeRunner(returncode=1, stderr="")

    with pytest.raises(RuntimeError) as exc:
        GitFileChangePreviewBuilder(runner=runner).build("/repo")

    assert "Unable to read git file changes" in str(exc.value)
