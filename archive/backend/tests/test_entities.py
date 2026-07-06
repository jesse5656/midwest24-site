from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_entities_returns_list():
    response = client.get("/entities")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
