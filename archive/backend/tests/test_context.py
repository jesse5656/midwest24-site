from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_entity_context():
    entity_response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "Context Test Entity",
            "description": "Entity used to test context endpoint",
        },
    )
    assert entity_response.status_code == 201
    entity = entity_response.json()

    response = client.get(f"/api/v1/context/{entity['id']}")

    assert response.status_code == 200

    data = response.json()
    assert data["entity"]["id"] == entity["id"]
    assert isinstance(data["relationships"], list)
    assert isinstance(data["tags"], list)
