from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_tag():
    response = client.post(
        "/api/v1/tags",
        json={"name": "test-tag"},
    )

    assert response.status_code in (201, 409)


def test_list_tags():
    response = client.get("/api/v1/tags")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
