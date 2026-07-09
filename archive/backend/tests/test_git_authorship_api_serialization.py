from app.api.git_authorship_preview import serialize_git_author_summary, serialize_git_authorship_preview
from app.connectors.repository import GitAuthorshipPreview, GitCommit


def make_commit(author_name="A", author_email="a@example.com", authored_at="2026-01-01T00:00:00Z"):
    return GitCommit(
        sha="abcdef",
        short_sha="abc",
        author_name=author_name,
        author_email=author_email,
        authored_at=authored_at,
        subject="Subject",
    )


def test_serialize_git_author_summary_returns_none_for_none():
    assert serialize_git_author_summary(None) is None


def test_serialize_git_author_summary_maps_fields():
    preview = GitAuthorshipPreview(commits=[make_commit()])

    response = serialize_git_author_summary(preview.authors[0])

    assert response.author_name == "A"
    assert response.identity == "A <a@example.com>"


def test_serialize_git_authorship_preview_maps_counts():
    preview = GitAuthorshipPreview(commits=[make_commit(), make_commit("B", "b@example.com")])

    response = serialize_git_authorship_preview(preview)

    assert response.commit_count == 2
    assert response.author_count == 2


def test_serialize_git_authorship_preview_maps_top_author():
    preview = GitAuthorshipPreview(commits=[make_commit(), make_commit()])

    response = serialize_git_authorship_preview(preview)

    assert response.top_author.author_name == "A"
    assert response.top_author.commit_count == 2


def test_serialize_git_authorship_preview_maps_empty_preview():
    response = serialize_git_authorship_preview(GitAuthorshipPreview())

    assert response.commit_count == 0
    assert response.author_count == 0
    assert response.top_author is None
    assert response.summary.outcome == "no_authorship"
