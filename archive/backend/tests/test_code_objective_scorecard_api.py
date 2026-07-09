from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_code_scorecard_api_returns_scorecard():
    response = client.post(
        "/api/v1/repository-code-objective-scorecard",
        json={"test_count": 645},
    )

    assert response.status_code == 200
    assert response.json()["objective_name"] == "Code Intelligence Preview"
    assert response.json()["test_count"] == 645
    assert response.json()["is_complete"] is True


def test_code_scorecard_api_returns_summary():
    response = client.post(
        "/api/v1/repository-code-objective-scorecard",
        json={"test_count": 645},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["outcome"] == "complete"


def test_code_scorecard_api_rejects_negative_test_count():
    response = client.post(
        "/api/v1/repository-code-objective-scorecard",
        json={"test_count": -1},
    )

    assert response.status_code == 422


def test_code_scorecard_api_requires_test_count():
    response = client.post(
        "/api/v1/repository-code-objective-scorecard",
        json={},
    )

    assert response.status_code == 422
