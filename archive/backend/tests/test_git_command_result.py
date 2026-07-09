from app.connectors.repository import GitCommandResult


def test_git_command_result_ok_when_returncode_zero():
    result = GitCommandResult(
        command=["git", "status"],
        cwd="/repo",
        returncode=0,
        stdout="",
        stderr="",
    )

    assert result.ok is True


def test_git_command_result_not_ok_when_returncode_nonzero():
    result = GitCommandResult(
        command=["git", "status"],
        cwd="/repo",
        returncode=1,
        stdout="",
        stderr="fatal",
    )

    assert result.ok is False
