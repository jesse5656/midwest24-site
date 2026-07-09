from app.api.git_commit_preview import serialize_git_commit, serialize_git_commit_preview
from app.connectors.repository import GitCommit, GitCommitPreview


def make_commit(sha="a", short_sha="a", author_name="A", author_email="a@example.com", subject="Subject"):
    return GitCommit(
        sha=sha,
        short_sha=short_sha,
        author_name=author_name,
        author_email=author_email,
        authored_at="2026-01-01T00:00:00Z",
        subject=subject,
    )


def test_serialize_git_commit_returns_none_for_none():
    assert serialize_git_commit(None) is None


def test_serialize_git_commit_maps_commit_fields():
    response = serialize_git_commit(make_commit(subject="Serialized"))

    assert response.subject == "Serialized"
    assert response.display == "a Serialized"


def test_serialize_git_commit_preview_maps_commit_count():
    preview = GitCommitPreview(commits=[make_commit(), make_commit(sha="b", short_sha="b")])

    response = serialize_git_commit_preview(preview)

    assert response.commit_count == 2
    assert len(response.commits) == 2


def test_serialize_git_commit_preview_maps_authors():
    preview = GitCommitPreview(
        commits=[
            make_commit(author_name="A", author_email="a@example.com"),
            make_commit(author_name="A", author_email="a@example.com"),
        ]
    )

    response = serialize_git_commit_preview(preview)

    assert response.authors[0].author_name == "A"
    assert response.authors[0].commit_count == 2


def test_serialize_git_commit_preview_maps_latest_and_oldest():
    first = make_commit(sha="a", short_sha="a", subject="First")
    second = make_commit(sha="b", short_sha="b", subject="Second")

    response = serialize_git_commit_preview(GitCommitPreview(commits=[first, second]))

    assert response.latest_commit.subject == "First"
    assert response.oldest_commit.subject == "Second"


def test_serialize_git_commit_preview_maps_summary():
    response = serialize_git_commit_preview(GitCommitPreview(commits=[make_commit()]))

    assert response.summary.outcome == "single_author_history"
