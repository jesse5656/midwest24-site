from fastapi.testclient import TestClient

import app.api.code_intelligence_report as report_api
from app.main import app
from tests.test_code_intelligence_report_models import make_report

client = TestClient(app)


class FakeCodeIntelligenceReportBuilder:
    def __init__(self, report=None, error=None):
        self.report = report
        self.error = error
        self.repository_path = None

    def build(self, repository_path):
        self.repository_path = repository_path

        if self.error:
            raise self.error

        return self.report


def test_code_intelligence_report_api_returns_report(monkeypatch):
    builder = FakeCodeIntelligenceReportBuilder(make_report())

    monkeypatch.setattr(report_api, "CodeIntelligenceReportBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-code-intelligence-report",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["outcome"] == "ready"
    assert response.json()["closeout"]["can_close"] is True
    assert builder.repository_path == "/repo"


def test_code_intelligence_report_api_returns_not_ready_report(monkeypatch):
    builder = FakeCodeIntelligenceReportBuilder(make_report(has_symbols=False))

    monkeypatch.setattr(report_api, "CodeIntelligenceReportBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-code-intelligence-report",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["is_ready"] is False


def test_code_intelligence_report_api_rejects_empty_path():
    response = client.post(
        "/api/v1/repository-code-intelligence-report",
        json={"repository_path": ""},
    )

    assert response.status_code == 422


def test_code_intelligence_report_api_maps_file_not_found_to_400(monkeypatch):
    builder = FakeCodeIntelligenceReportBuilder(error=FileNotFoundError("missing repo"))

    monkeypatch.setattr(report_api, "CodeIntelligenceReportBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-code-intelligence-report",
        json={"repository_path": "/missing"},
    )

    assert response.status_code == 400
    assert "missing repo" in response.json()["detail"]


def test_code_intelligence_report_api_maps_value_error_to_400(monkeypatch):
    builder = FakeCodeIntelligenceReportBuilder(error=ValueError("bad repo"))

    monkeypatch.setattr(report_api, "CodeIntelligenceReportBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-code-intelligence-report",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "bad repo" in response.json()["detail"]
