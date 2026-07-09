from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_archive_backend_health_api_returns_healthy_report():
    response = client.post(
        "/api/v1/archive-backend-health",
        json={"test_count": 684},
    )

    assert response.status_code == 200
    assert response.json()["passed"] is True
    assert response.json()["summary"]["outcome"] == "healthy"


def test_archive_backend_health_api_returns_unhealthy_without_tests():
    response = client.post(
        "/api/v1/archive-backend-health",
        json={"test_count": 0},
    )

    assert response.status_code == 200
    assert response.json()["passed"] is False
    assert response.json()["summary"]["outcome"] == "unhealthy"


def test_archive_backend_health_api_returns_warning_state():
    response = client.post(
        "/api/v1/archive-backend-health",
        json={
            "test_count": 684,
            "has_runbook": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["summary"]["outcome"] == "warnings"


def test_archive_backend_health_api_rejects_negative_test_count():
    response = client.post(
        "/api/v1/archive-backend-health",
        json={"test_count": -1},
    )

    assert response.status_code == 422


def test_archive_backend_health_api_reports_failed_check_names():
    response = client.post(
        "/api/v1/archive-backend-health",
        json={
            "test_count": 684,
            "has_progress_ledger": False,
        },
    )

    failed_names = [
        check["name"]
        for check in response.json()["checks"]
        if not check["passed"]
    ]

    assert "progress_ledger_present" in failed_names
