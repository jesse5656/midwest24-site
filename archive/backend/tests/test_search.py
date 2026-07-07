from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_entities():
    client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "Searchable Insurance SOP",
            "description": "Procedure for claim documentation",
        },
    )

    response = client.get("/api/v1/search/entities?q=insurance")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1
