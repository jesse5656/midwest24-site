import pytest

from app.connectors.repository import GitCommitParser


def test_git_commit_parser_parses_single_line():
    line = "abcdef123456\x1fabcdef1\x1fJesse\x1fjesse@example.com\x1f2026-07-09T10:00:00Z\x1fInitial commit"

    commit = GitCommitParser().parse_line(line)

    assert commit.sha == "abcdef123456"
    assert commit.short_sha == "abcdef1"
    assert commit.author_name == "Jesse"
    assert commit.author_email == "jesse@example.com"
    assert commit.authored_at == "2026-07-09T10:00:00Z"
    assert commit.subject == "Initial commit"


def test_git_commit_parser_display_combines_short_sha_and_subject():
    line = "abcdef123456\x1fabcdef1\x1fJesse\x1fjesse@example.com\x1f2026-07-09T10:00:00Z\x1fInitial commit"

    commit = GitCommitParser().parse_line(line)

    assert commit.display == "abcdef1 Initial commit"


def test_git_commit_parser_parses_multiple_lines():
    text = "\n".join(
        [
            "a\x1fa\x1fA\x1fa@example.com\x1f2026-01-01T00:00:00Z\x1fOne",
            "b\x1fb\x1fB\x1fb@example.com\x1f2026-01-02T00:00:00Z\x1fTwo",
        ]
    )

    commits = GitCommitParser().parse_lines(text)

    assert [commit.subject for commit in commits] == ["One", "Two"]


def test_git_commit_parser_ignores_blank_lines():
    text = "\n\na\x1fa\x1fA\x1fa@example.com\x1f2026-01-01T00:00:00Z\x1fOne\n\n"

    commits = GitCommitParser().parse_lines(text)

    assert len(commits) == 1


def test_git_commit_parser_rejects_invalid_line():
    with pytest.raises(ValueError):
        GitCommitParser().parse_line("not enough fields")
