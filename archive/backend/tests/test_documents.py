from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_document_to_entity():
    entity_response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "Document Upload Test Entity",
        },
    )
    assert entity_response.status_code == 201
    entity = entity_response.json()

    response = client.post(
        f"/api/v1/entities/{entity['id']}/documents",
        files={
            "file": (
                "test-document.txt",
                BytesIO(b"Test document content"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["entity_id"] == entity["id"]
    assert data["filename"] == "test-document.txt"
    assert data["mime_type"] == "text/plain"
    assert "storage_path" in data


def test_list_entity_documents():
    entity_response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "Document List Test Entity",
        },
    )
    assert entity_response.status_code == 201
    entity = entity_response.json()

    response = client.get(f"/api/v1/entities/{entity['id']}/documents")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
