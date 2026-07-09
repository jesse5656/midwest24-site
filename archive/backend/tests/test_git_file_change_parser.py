import pytest

from app.connectors.repository import GitFileChangeParser


def test_git_file_change_parser_parses_single_commit_with_file():
    text = "\x1eabcdef\x1fabc\x1fSubject\nM\tREADME.md\n"

    preview = GitFileChangeParser().parse(text)

    assert preview.commit_count == 1
    assert preview.commits[0].commit_sha == "abcdef"
    assert preview.commits[0].files[0].status == "M"
    assert preview.commits[0].files[0].path == "README.md"


def test_git_file_change_parser_parses_multiple_commits():
    text = "\x1ea\x1fa\x1fA\nA\tA.md\n\x1eb\x1fb\x1fB\nD\tB.md\n"

    preview = GitFileChangeParser().parse(text)

    assert preview.commit_count == 2
    assert preview.commits[0].added_count == 1
    assert preview.commits[1].deleted_count == 1


def test_git_file_change_parser_handles_commit_without_files():
    text = "\x1ea\x1fa\x1fA\n"

    preview = GitFileChangeParser().parse(text)

    assert preview.commit_count == 1
    assert preview.commits[0].file_count == 0


def test_git_file_change_parser_ignores_blank_blocks():
    text = "\n\n\x1ea\x1fa\x1fA\nM\tREADME.md\n\n"

    preview = GitFileChangeParser().parse(text)

    assert preview.commit_count == 1


def test_git_file_change_parser_parses_rename_using_new_path():
    text = "\x1ea\x1fa\x1fRename\nR100\told.md\tnew.md\n"

    preview = GitFileChangeParser().parse(text)

    assert preview.commits[0].files[0].status == "R100"
    assert preview.commits[0].files[0].path == "new.md"


def test_git_file_change_parser_rejects_bad_header():
    with pytest.raises(ValueError):
        GitFileChangeParser().parse("\x1ebad-header\nM\tREADME.md\n")


def test_git_file_change_parser_rejects_bad_file_line():
    with pytest.raises(ValueError):
        GitFileChangeParser().parse("\x1ea\x1fa\x1fA\nbadline\n")
