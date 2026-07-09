from pathlib import Path

from fastapi.testclient import TestClient

import app.api.git_repository_intelligence as git_api
from app.connectors.repository import GitRepositorySummary
from app.main import app

client = TestClient(app)


class FakeSummaryBuilder:
    def __init__(self, summary=None, error=None):
        self.summary = summary
        self.error = error
        self.repository_path = None
        self.commit_limit = None

    def build(self, repository_path, commit_limit=5):
        self.repository_path = repository_path
        self.commit_limit = commit_limit

        if self.error:
            raise self.error

        return self.summary


def test_git_repository_intelligence_api_returns_clean_repository_summary(monkeypatch):
    builder = FakeSummaryBuilder(
        GitRepositorySummary(
            is_repository=True,
            root="/repo",
            current_branch="main",
            recent_commit_count=5,
            is_clean=True,
        )
    )

    monkeypatch.setattr(git_api, "GitRepositorySummaryBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-intelligence",
        json={"repository_path": "/repo", "commit_limit": 5},
    )

    assert response.status_code == 200
    assert response.json()["intelligence"]["current_branch"] == "main"
    assert response.json()["summary"]["outcome"] == "repository_clean"
    assert builder.repository_path == "/repo"
    assert builder.commit_limit == 5


def test_git_repository_intelligence_api_returns_non_repository_summary(monkeypatch):
    builder = FakeSummaryBuilder(
        GitRepositorySummary(
            is_repository=False,
            root=None,
            current_branch=None,
            recent_commit_count=0,
            is_clean=None,
        )
    )

    monkeypatch.setattr(git_api, "GitRepositorySummaryBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-intelligence",
        json={"repository_path": "/not-repo"},
    )

    assert response.status_code == 200
    assert response.json()["intelligence"]["is_repository"] is False
    assert response.json()["summary"]["outcome"] == "not_git_repository"


def test_git_repository_intelligence_api_returns_dirty_repository_summary(monkeypatch):
    builder = FakeSummaryBuilder(
        GitRepositorySummary(
            is_repository=True,
            root="/repo",
            current_branch="main",
            recent_commit_count=2,
            is_clean=False,
        )
    )

    monkeypatch.setattr(git_api, "GitRepositorySummaryBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-intelligence",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["outcome"] == "repository_has_changes"


def test_git_repository_intelligence_api_rejects_empty_path():
    response = client.post(
        "/api/v1/repository-git-intelligence",
        json={"repository_path": ""},
    )

    assert response.status_code == 422


def test_git_repository_intelligence_api_rejects_zero_commit_limit():
    response = client.post(
        "/api/v1/repository-git-intelligence",
        json={"repository_path": "/repo", "commit_limit": 0},
    )

    assert response.status_code == 422


def test_git_repository_intelligence_api_rejects_commit_limit_over_50():
    response = client.post(
        "/api/v1/repository-git-intelligence",
        json={"repository_path": "/repo", "commit_limit": 51},
    )

    assert response.status_code == 422


def test_git_repository_intelligence_api_maps_file_not_found_to_400(monkeypatch):
    builder = FakeSummaryBuilder(error=FileNotFoundError("missing"))

    monkeypatch.setattr(git_api, "GitRepositorySummaryBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-intelligence",
        json={"repository_path": "/missing"},
    )

    assert response.status_code == 400
    assert "missing" in response.json()["detail"]


def test_git_repository_intelligence_api_maps_runtime_error_to_400(monkeypatch):
    builder = FakeSummaryBuilder(error=RuntimeError("git failed"))

    monkeypatch.setattr(git_api, "GitRepositorySummaryBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-intelligence",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "git failed" in response.json()["detail"]
