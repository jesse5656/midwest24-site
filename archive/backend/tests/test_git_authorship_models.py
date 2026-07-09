from app.connectors.repository import GitAuthorshipPreview, GitCommit


def make_commit(author_name="A", author_email="a@example.com", authored_at="2026-01-01T00:00:00Z"):
    return GitCommit(
        sha=authored_at,
        short_sha=authored_at[:7],
        author_name=author_name,
        author_email=author_email,
        authored_at=authored_at,
        subject="Subject",
    )


def test_authorship_preview_counts_commits():
    preview = GitAuthorshipPreview(commits=[make_commit(), make_commit()])

    assert preview.commit_count == 2


def test_authorship_preview_counts_unique_authors():
    preview = GitAuthorshipPreview(
        commits=[
            make_commit("A", "a@example.com"),
            make_commit("A", "a@example.com"),
            make_commit("B", "b@example.com"),
        ]
    )

    assert preview.author_count == 2


def test_authorship_preview_groups_author_commit_counts():
    preview = GitAuthorshipPreview(
        commits=[
            make_commit("A", "a@example.com"),
            make_commit("A", "a@example.com"),
            make_commit("B", "b@example.com"),
        ]
    )

    authors = preview.authors

    assert authors[0].author_name == "A"
    assert authors[0].commit_count == 2
    assert authors[1].author_name == "B"
    assert authors[1].commit_count == 1


def test_authorship_preview_sorts_authors_by_count_then_name():
    preview = GitAuthorshipPreview(
        commits=[
            make_commit("Z", "z@example.com"),
            make_commit("A", "a@example.com"),
        ]
    )

    assert [author.author_name for author in preview.authors] == ["A", "Z"]


def test_authorship_preview_top_author_returns_highest_commit_count():
    preview = GitAuthorshipPreview(
        commits=[
            make_commit("B", "b@example.com"),
            make_commit("A", "a@example.com"),
            make_commit("A", "a@example.com"),
        ]
    )

    assert preview.top_author.author_name == "A"
    assert preview.top_author.commit_count == 2


def test_authorship_preview_top_author_none_when_no_commits():
    assert GitAuthorshipPreview().top_author is None


def test_authorship_preview_first_and_last_authored_dates():
    preview = GitAuthorshipPreview(
        commits=[
            make_commit(authored_at="2026-01-03T00:00:00Z"),
            make_commit(authored_at="2026-01-01T00:00:00Z"),
            make_commit(authored_at="2026-01-02T00:00:00Z"),
        ]
    )

    assert preview.first_authored_at == "2026-01-01T00:00:00Z"
    assert preview.last_authored_at == "2026-01-03T00:00:00Z"


def test_authorship_preview_dates_none_when_empty():
    preview = GitAuthorshipPreview()

    assert preview.first_authored_at is None
    assert preview.last_authored_at is None


def test_author_summary_identity_formats_name_and_email():
    preview = GitAuthorshipPreview(commits=[make_commit("A", "a@example.com")])

    assert preview.authors[0].identity == "A <a@example.com>"


def test_author_summary_tracks_first_and_last_author_dates():
    preview = GitAuthorshipPreview(
        commits=[
            make_commit("A", "a@example.com", "2026-01-03T00:00:00Z"),
            make_commit("A", "a@example.com", "2026-01-01T00:00:00Z"),
        ]
    )

    author = preview.authors[0]

    assert author.first_authored_at == "2026-01-01T00:00:00Z"
    assert author.last_authored_at == "2026-01-03T00:00:00Z"
