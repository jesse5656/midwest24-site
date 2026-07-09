from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_backend_milestone_api_returns_scorecard():
    response = client.post(
        "/api/v1/archive-backend-milestone-scorecard",
        json={"test_count": 721},
    )

    assert response.status_code == 200
    assert response.json()["milestone_name"] == "Archive Backend Milestone"
    assert response.json()["test_count"] == 721


def test_backend_milestone_api_returns_complete_summary():
    response = client.post(
        "/api/v1/archive-backend-milestone-scorecard",
        json={"test_count": 721},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["outcome"] == "complete"


def test_backend_milestone_api_returns_ready_closeout():
    response = client.post(
        "/api/v1/archive-backend-milestone-scorecard",
        json={"test_count": 721},
    )

    assert response.status_code == 200
    assert response.json()["closeout"]["can_close"] is True


def test_backend_milestone_api_rejects_negative_test_count():
    response = client.post(
        "/api/v1/archive-backend-milestone-scorecard",
        json={"test_count": -1},
    )

    assert response.status_code == 422


def test_backend_milestone_api_requires_test_count():
    response = client.post(
        "/api/v1/archive-backend-milestone-scorecard",
        json={},
    )

    assert response.status_code == 422
