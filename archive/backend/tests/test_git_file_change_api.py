from fastapi.testclient import TestClient

import app.api.git_file_change_preview as file_change_api
from app.connectors.repository import GitCommitFileChangeSet, GitFileChange, GitFileChangePreview
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


def make_preview():
    return GitFileChangePreview(
        commits=[
            GitCommitFileChangeSet(
                commit_sha="abcdef",
                short_sha="abc",
                subject="Subject",
                files=[GitFileChange(status="M", path="README.md")],
            )
        ]
    )


def test_git_file_change_preview_api_returns_preview(monkeypatch):
    builder = FakePreviewBuilder(make_preview())

    monkeypatch.setattr(file_change_api, "GitFileChangePreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-file-change-preview",
        json={"repository_path": "/repo", "limit": 5},
    )

    assert response.status_code == 200
    assert response.json()["file_change_count"] == 1
    assert response.json()["commits"][0]["files"][0]["path"] == "README.md"
    assert builder.repository_path == "/repo"
    assert builder.limit == 5


def test_git_file_change_preview_api_returns_empty_preview(monkeypatch):
    builder = FakePreviewBuilder(GitFileChangePreview())

    monkeypatch.setattr(file_change_api, "GitFileChangePreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-file-change-preview",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["outcome"] == "no_file_changes"


def test_git_file_change_preview_api_rejects_empty_path():
    response = client.post(
        "/api/v1/repository-git-file-change-preview",
        json={"repository_path": ""},
    )

    assert response.status_code == 422


def test_git_file_change_preview_api_rejects_zero_limit():
    response = client.post(
        "/api/v1/repository-git-file-change-preview",
        json={"repository_path": "/repo", "limit": 0},
    )

    assert response.status_code == 422


def test_git_file_change_preview_api_rejects_limit_over_100():
    response = client.post(
        "/api/v1/repository-git-file-change-preview",
        json={"repository_path": "/repo", "limit": 101},
    )

    assert response.status_code == 422


def test_git_file_change_preview_api_maps_runtime_error_to_400(monkeypatch):
    builder = FakePreviewBuilder(error=RuntimeError("git file changes failed"))

    monkeypatch.setattr(file_change_api, "GitFileChangePreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-file-change-preview",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "git file changes failed" in response.json()["detail"]


def test_git_file_change_preview_api_maps_value_error_to_400(monkeypatch):
    builder = FakePreviewBuilder(error=ValueError("bad file change preview"))

    monkeypatch.setattr(file_change_api, "GitFileChangePreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-file-change-preview",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "bad file change preview" in response.json()["detail"]
