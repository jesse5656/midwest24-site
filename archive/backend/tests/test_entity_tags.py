from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_attach_tag_to_entity():
    entity_response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "Tagged Test Entity",
        },
    )
    assert entity_response.status_code == 201
    entity = entity_response.json()

    tag_response = client.post(
        "/api/v1/tags",
        json={"name": f"entity-tag-{entity['id'][:8]}"},
    )
    assert tag_response.status_code == 201
    tag = tag_response.json()

    response = client.post(
        "/api/v1/entity-tags",
        json={
            "entity_id": entity["id"],
            "tag_id": tag["id"],
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["entity_id"] == entity["id"]
    assert data["tag_id"] == tag["id"]


def test_list_entity_tags():
    entity_response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "List Tags Entity",
        },
    )
    assert entity_response.status_code == 201
    entity = entity_response.json()

    response = client.get(f"/api/v1/entities/{entity['id']}/tags")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
