from app.connectors.repository import GitCommit, GitCommitPreview, GitCommitPreviewBuilder


def make_commit(sha="a", short_sha="a", author_name="A", author_email="a@example.com", subject="Subject"):
    return GitCommit(
        sha=sha,
        short_sha=short_sha,
        author_name=author_name,
        author_email=author_email,
        authored_at="2026-01-01T00:00:00Z",
        subject=subject,
    )


class FakeHistoryReader:
    def __init__(self, commits):
        self.commits = commits
        self.repository_path = None
        self.limit = None

    def recent_commits(self, repository_path, limit=10):
        self.repository_path = repository_path
        self.limit = limit
        return self.commits


def test_git_commit_preview_counts_commits():
    preview = GitCommitPreview(commits=[make_commit(), make_commit(sha="b", short_sha="b")])

    assert preview.commit_count == 2


def test_git_commit_preview_latest_commit_is_first():
    first = make_commit(sha="a", short_sha="a", subject="First")
    second = make_commit(sha="b", short_sha="b", subject="Second")

    preview = GitCommitPreview(commits=[first, second])

    assert preview.latest_commit == first


def test_git_commit_preview_oldest_commit_is_last():
    first = make_commit(sha="a", short_sha="a", subject="First")
    second = make_commit(sha="b", short_sha="b", subject="Second")

    preview = GitCommitPreview(commits=[first, second])

    assert preview.oldest_commit == second


def test_git_commit_preview_latest_and_oldest_none_when_empty():
    preview = GitCommitPreview()

    assert preview.latest_commit is None
    assert preview.oldest_commit is None


def test_git_commit_preview_groups_authors_by_name_and_email():
    preview = GitCommitPreview(
        commits=[
            make_commit(author_name="A", author_email="a@example.com"),
            make_commit(author_name="A", author_email="a@example.com"),
            make_commit(author_name="B", author_email="b@example.com"),
        ]
    )

    authors = preview.authors

    assert authors[0].author_name == "A"
    assert authors[0].commit_count == 2
    assert authors[1].author_name == "B"
    assert authors[1].commit_count == 1


def test_git_commit_preview_sorts_authors_by_commit_count_then_name():
    preview = GitCommitPreview(
        commits=[
            make_commit(author_name="Z", author_email="z@example.com"),
            make_commit(author_name="A", author_email="a@example.com"),
        ]
    )

    assert [author.author_name for author in preview.authors] == ["A", "Z"]


def test_git_commit_preview_builder_uses_history_reader():
    reader = FakeHistoryReader([make_commit(subject="Built")])

    preview = GitCommitPreviewBuilder(history_reader=reader).build("/repo", limit=7)

    assert preview.commit_count == 1
    assert preview.commits[0].subject == "Built"
    assert reader.repository_path == "/repo"
    assert reader.limit == 7
