from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_entity():
    response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "Test Entity",
            "description": "Created by automated test",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["entity_type"] == "document"
    assert data["title"] == "Test Entity"
    assert data["description"] == "Created by automated test"
    assert data["status"] == "active"
    assert "id" in data


def test_list_entities():
    response = client.get("/api/v1/entities")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
