from fastapi.testclient import TestClient

import app.api.git_authorship_preview as authorship_api
from app.connectors.repository import GitAuthorshipPreview, GitCommit
from app.main import app

client = TestClient(app)


class FakeAuthorshipBuilder:
    def __init__(self, preview=None, error=None):
        self.preview = preview
        self.error = error
        self.repository_path = None
        self.limit = None

    def build(self, repository_path, limit=50):
        self.repository_path = repository_path
        self.limit = limit

        if self.error:
            raise self.error

        return self.preview


def make_commit(author_name="A", author_email="a@example.com"):
    return GitCommit(
        sha="abcdef",
        short_sha="abc",
        author_name=author_name,
        author_email=author_email,
        authored_at="2026-01-01T00:00:00Z",
        subject="Subject",
    )


def test_authorship_api_returns_preview(monkeypatch):
    builder = FakeAuthorshipBuilder(GitAuthorshipPreview(commits=[make_commit()]))

    monkeypatch.setattr(authorship_api, "GitAuthorshipPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-authorship-preview",
        json={"repository_path": "/repo", "limit": 25},
    )

    assert response.status_code == 200
    assert response.json()["commit_count"] == 1
    assert response.json()["author_count"] == 1
    assert builder.repository_path == "/repo"
    assert builder.limit == 25


def test_authorship_api_returns_empty_preview(monkeypatch):
    builder = FakeAuthorshipBuilder(GitAuthorshipPreview())

    monkeypatch.setattr(authorship_api, "GitAuthorshipPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-authorship-preview",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["outcome"] == "no_authorship"


def test_authorship_api_rejects_empty_path():
    response = client.post(
        "/api/v1/repository-git-authorship-preview",
        json={"repository_path": ""},
    )

    assert response.status_code == 422


def test_authorship_api_rejects_zero_limit():
    response = client.post(
        "/api/v1/repository-git-authorship-preview",
        json={"repository_path": "/repo", "limit": 0},
    )

    assert response.status_code == 422


def test_authorship_api_rejects_limit_over_250():
    response = client.post(
        "/api/v1/repository-git-authorship-preview",
        json={"repository_path": "/repo", "limit": 251},
    )

    assert response.status_code == 422


def test_authorship_api_maps_runtime_error_to_400(monkeypatch):
    builder = FakeAuthorshipBuilder(error=RuntimeError("git authorship failed"))

    monkeypatch.setattr(authorship_api, "GitAuthorshipPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-authorship-preview",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "git authorship failed" in response.json()["detail"]


def test_authorship_api_maps_value_error_to_400(monkeypatch):
    builder = FakeAuthorshipBuilder(error=ValueError("bad authorship preview"))

    monkeypatch.setattr(authorship_api, "GitAuthorshipPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-authorship-preview",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "bad authorship preview" in response.json()["detail"]
