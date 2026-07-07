from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_entity(title: str, entity_type: str = "document") -> dict:
    response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": entity_type,
            "title": title,
            "description": "Relationship test entity",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_relationship():
    source = create_entity("Relationship Source")
    target = create_entity("Relationship Target", "evidence")

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_entity_id": source["id"],
            "target_entity_id": target["id"],
            "relationship_type": "SUPPORTS",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["source_entity_id"] == source["id"]
    assert data["target_entity_id"] == target["id"]
    assert data["relationship_type"] == "SUPPORTS"


def test_list_relationships():
    response = client.get("/api/v1/relationships")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_entity_relationships():
    source = create_entity("Entity Relationship Source")
    target = create_entity("Entity Relationship Target", "evidence")

    create_response = client.post(
        "/api/v1/relationships",
        json={
            "source_entity_id": source["id"],
            "target_entity_id": target["id"],
            "relationship_type": "REFERENCES",
        },
    )
    assert create_response.status_code == 201

    response = client.get(f"/api/v1/entities/{source['id']}/relationships")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
