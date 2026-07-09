from app.connectors.repository import GitCommitFileChangeSet, GitFileChange, GitFileChangePreview


def test_git_file_change_identifies_added_file():
    change = GitFileChange(status="A", path="README.md")

    assert change.is_added is True
    assert change.is_modified is False
    assert change.is_deleted is False
    assert change.is_renamed is False


def test_git_file_change_identifies_modified_file():
    change = GitFileChange(status="M", path="README.md")

    assert change.is_modified is True


def test_git_file_change_identifies_deleted_file():
    change = GitFileChange(status="D", path="README.md")

    assert change.is_deleted is True


def test_git_file_change_identifies_renamed_file():
    change = GitFileChange(status="R100", path="README.md")

    assert change.is_renamed is True


def test_commit_file_change_set_counts_statuses():
    commit = GitCommitFileChangeSet(
        commit_sha="abc",
        short_sha="abc",
        subject="Change files",
        files=[
            GitFileChange(status="A", path="a.md"),
            GitFileChange(status="M", path="m.md"),
            GitFileChange(status="D", path="d.md"),
            GitFileChange(status="R100", path="new.md"),
        ],
    )

    assert commit.file_count == 4
    assert commit.added_count == 1
    assert commit.modified_count == 1
    assert commit.deleted_count == 1
    assert commit.renamed_count == 1


def test_file_change_preview_counts_totals():
    preview = GitFileChangePreview(
        commits=[
            GitCommitFileChangeSet(
                commit_sha="a",
                short_sha="a",
                subject="A",
                files=[GitFileChange(status="A", path="a.md")],
            ),
            GitCommitFileChangeSet(
                commit_sha="b",
                short_sha="b",
                subject="B",
                files=[GitFileChange(status="M", path="b.md")],
            ),
        ]
    )

    assert preview.commit_count == 2
    assert preview.file_change_count == 2
    assert preview.added_count == 1
    assert preview.modified_count == 1


def test_file_change_preview_returns_sorted_touched_paths():
    preview = GitFileChangePreview(
        commits=[
            GitCommitFileChangeSet(
                commit_sha="a",
                short_sha="a",
                subject="A",
                files=[
                    GitFileChange(status="M", path="z.md"),
                    GitFileChange(status="M", path="a.md"),
                    GitFileChange(status="M", path="a.md"),
                ],
            )
        ]
    )

    assert preview.touched_paths == ["a.md", "z.md"]
