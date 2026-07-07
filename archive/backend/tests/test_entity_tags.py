from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_attach_tag_to_entity():
    entity = client.post(
        "/api/v1/entities",
        json={"entity_type": "document", "title": "Tagged Test Entity"},
    ).json()

    tag = client.post(
        "/api/v1/tags",
        json={"name": "entity-tag-test"},
    ).json()

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
    entity = client.post(
        "/api/v1/entities",
        json={"entity_type": "document", "title": "List Tags Entity"},
    ).json()

    response = client.get(f"/api/v1/entities/{entity['id']}/tags")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
