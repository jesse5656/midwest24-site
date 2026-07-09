from fastapi.testclient import TestClient

import app.api.git_intelligence_report as report_api
from app.main import app
from tests.test_git_intelligence_report_models import make_report

client = TestClient(app)


class FakeReportBuilder:
    def __init__(self, report=None, error=None):
        self.report = report
        self.error = error
        self.repository_path = None
        self.limit = None

    def build(self, repository_path, limit=25):
        self.repository_path = repository_path
        self.limit = limit

        if self.error:
            raise self.error

        return self.report


def test_git_intelligence_report_api_returns_report(monkeypatch):
    builder = FakeReportBuilder(make_report())

    monkeypatch.setattr(report_api, "GitIntelligenceReportBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-intelligence-report",
        json={"repository_path": "/repo", "limit": 25},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["outcome"] == "ready"
    assert response.json()["closeout"]["can_close"] is True
    assert builder.repository_path == "/repo"
    assert builder.limit == 25


def test_git_intelligence_report_api_rejects_empty_path():
    response = client.post(
        "/api/v1/repository-git-intelligence-report",
        json={"repository_path": ""},
    )

    assert response.status_code == 422


def test_git_intelligence_report_api_rejects_zero_limit():
    response = client.post(
        "/api/v1/repository-git-intelligence-report",
        json={"repository_path": "/repo", "limit": 0},
    )

    assert response.status_code == 422


def test_git_intelligence_report_api_rejects_limit_over_100():
    response = client.post(
        "/api/v1/repository-git-intelligence-report",
        json={"repository_path": "/repo", "limit": 101},
    )

    assert response.status_code == 422


def test_git_intelligence_report_api_maps_runtime_error_to_400(monkeypatch):
    builder = FakeReportBuilder(error=RuntimeError("git intelligence failed"))

    monkeypatch.setattr(report_api, "GitIntelligenceReportBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-git-intelligence-report",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "git intelligence failed" in response.json()["detail"]
