from fastapi.testclient import TestClient

import app.api.git_commit_preview as preview_api
from app.connectors.repository import GitCommit, GitCommitPreview
from app.main import app

client = TestClient(app)


class FakePreviewBuilder:
    def __init__(self, preview=None, error=None):
        self.preview = preview
        self.error = error
        self.repository_path = None
        self.limit = None

    def build(self, repository_path, limit=10):
        self.repository_path = repository_path
        self.limit = limit

        if self.error:
            raise self.error

        return self.preview


def make_commit(subject="Subject"):
    return GitCommit(
        sha="abcdef",
        short_sha="abc",
        author_name="A",
        author_email="a@example.com",
        authored_at="2026-01-01T00:00:00Z",
        subject=subject,
    )


def test_git_commit_preview_api_returns_preview(monkeypatch):
    builder = FakePreviewBuilder(GitCommitPreview(commits=[make_commit("API")]))

    monkeypatch.setattr(preview_api, "GitCommitPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-commit-preview",
        json={"repository_path": "/repo", "limit": 5},
    )

    assert response.status_code == 200
    assert response.json()["commit_count"] == 1
    assert response.json()["commits"][0]["subject"] == "API"
    assert builder.repository_path == "/repo"
    assert builder.limit == 5


def test_git_commit_preview_api_returns_empty_preview(monkeypatch):
    builder = FakePreviewBuilder(GitCommitPreview())

    monkeypatch.setattr(preview_api, "GitCommitPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-commit-preview",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["commit_count"] == 0
    assert response.json()["summary"]["outcome"] == "no_commits"


def test_git_commit_preview_api_rejects_empty_path():
    response = client.post(
        "/api/v1/repository-git-commit-preview",
        json={"repository_path": ""},
    )

    assert response.status_code == 422


def test_git_commit_preview_api_rejects_zero_limit():
    response = client.post(
        "/api/v1/repository-git-commit-preview",
        json={"repository_path": "/repo", "limit": 0},
    )

    assert response.status_code == 422


def test_git_commit_preview_api_rejects_limit_over_100():
    response = client.post(
        "/api/v1/repository-git-commit-preview",
        json={"repository_path": "/repo", "limit": 101},
    )

    assert response.status_code == 422


def test_git_commit_preview_api_maps_runtime_error_to_400(monkeypatch):
    builder = FakePreviewBuilder(error=RuntimeError("git log failed"))

    monkeypatch.setattr(preview_api, "GitCommitPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-commit-preview",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "git log failed" in response.json()["detail"]


def test_git_commit_preview_api_maps_value_error_to_400(monkeypatch):
    builder = FakePreviewBuilder(error=ValueError("bad limit"))

    monkeypatch.setattr(preview_api, "GitCommitPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-commit-preview",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "bad limit" in response.json()["detail"]
