from fastapi.testclient import TestClient

import app.api.git_branch_analysis as branch_api
from app.connectors.repository import GitBranch, GitBranchAnalysis
from app.main import app

client = TestClient(app)


class FakeBranchAnalysisBuilder:
    def __init__(self, analysis=None, error=None):
        self.analysis = analysis
        self.error = error
        self.repository_path = None

    def build(self, repository_path):
        self.repository_path = repository_path

        if self.error:
            raise self.error

        return self.analysis


def test_branch_analysis_api_returns_analysis(monkeypatch):
    builder = FakeBranchAnalysisBuilder(
        GitBranchAnalysis(
            branches=[
                GitBranch(name="main", current=True),
                GitBranch(name="dev"),
            ]
        )
    )

    monkeypatch.setattr(branch_api, "GitBranchAnalysisBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-branch-analysis",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["branch_count"] == 2
    assert response.json()["current_branch_name"] == "main"
    assert builder.repository_path == "/repo"


def test_branch_analysis_api_returns_empty_analysis(monkeypatch):
    builder = FakeBranchAnalysisBuilder(GitBranchAnalysis())

    monkeypatch.setattr(branch_api, "GitBranchAnalysisBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-branch-analysis",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["outcome"] == "no_branches"


def test_branch_analysis_api_rejects_empty_path():
    response = client.post(
        "/api/v1/repository-git-branch-analysis",
        json={"repository_path": ""},
    )

    assert response.status_code == 422


def test_branch_analysis_api_maps_runtime_error_to_400(monkeypatch):
    builder = FakeBranchAnalysisBuilder(error=RuntimeError("git branch failed"))

    monkeypatch.setattr(branch_api, "GitBranchAnalysisBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-branch-analysis",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "git branch failed" in response.json()["detail"]


def test_branch_analysis_api_maps_value_error_to_400(monkeypatch):
    builder = FakeBranchAnalysisBuilder(error=ValueError("bad branch analysis"))

    monkeypatch.setattr(branch_api, "GitBranchAnalysisBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-branch-analysis",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "bad branch analysis" in response.json()["detail"]
