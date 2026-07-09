from app.api.git_file_change_preview import (
    serialize_git_commit_file_change_set,
    serialize_git_file_change,
    serialize_git_file_change_preview,
)
from app.connectors.repository import GitCommitFileChangeSet, GitFileChange, GitFileChangePreview


def test_serialize_git_file_change_maps_flags():
    response = serialize_git_file_change(GitFileChange(status="A", path="README.md"))

    assert response.status == "A"
    assert response.path == "README.md"
    assert response.is_added is True


def test_serialize_git_commit_file_change_set_maps_counts():
    commit = GitCommitFileChangeSet(
        commit_sha="abcdef",
        short_sha="abc",
        subject="Subject",
        files=[
            GitFileChange(status="A", path="A.md"),
            GitFileChange(status="M", path="M.md"),
        ],
    )

    response = serialize_git_commit_file_change_set(commit)

    assert response.file_count == 2
    assert response.added_count == 1
    assert response.modified_count == 1


def test_serialize_git_file_change_preview_maps_totals_and_summary():
    preview = GitFileChangePreview(
        commits=[
            GitCommitFileChangeSet(
                commit_sha="abcdef",
                short_sha="abc",
                subject="Subject",
                files=[GitFileChange(status="M", path="README.md")],
            )
        ]
    )

    response = serialize_git_file_change_preview(preview)

    assert response.commit_count == 1
    assert response.file_change_count == 1
    assert response.touched_paths == ["README.md"]
    assert response.summary.outcome == "file_changes_found"


def test_serialize_empty_git_file_change_preview_maps_no_change_summary():
    response = serialize_git_file_change_preview(GitFileChangePreview())

    assert response.commit_count == 0
    assert response.file_change_count == 0
    assert response.summary.outcome == "no_file_changes"
