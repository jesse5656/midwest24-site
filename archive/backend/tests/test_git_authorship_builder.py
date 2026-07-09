from app.connectors.repository import GitAuthorshipPreviewBuilder, GitCommit


class FakeHistoryReader:
    def __init__(self, commits):
        self.commits = commits
        self.repository_path = None
        self.limit = None

    def recent_commits(self, repository_path, limit=50):
        self.repository_path = repository_path
        self.limit = limit
        return self.commits


def make_commit():
    return GitCommit(
        sha="abcdef",
        short_sha="abc",
        author_name="A",
        author_email="a@example.com",
        authored_at="2026-01-01T00:00:00Z",
        subject="Subject",
    )


def test_authorship_preview_builder_uses_history_reader():
    reader = FakeHistoryReader([make_commit()])

    preview = GitAuthorshipPreviewBuilder(history_reader=reader).build("/repo", limit=12)

    assert preview.commit_count == 1
    assert reader.repository_path == "/repo"
    assert reader.limit == 12


def test_authorship_preview_builder_returns_empty_preview():
    reader = FakeHistoryReader([])

    preview = GitAuthorshipPreviewBuilder(history_reader=reader).build("/repo")

    assert preview.commit_count == 0
    assert preview.author_count == 0
