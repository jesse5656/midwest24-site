from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_document() -> dict:
    entity_response = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "Processing Job Test Entity",
        },
    )
    assert entity_response.status_code == 201
    entity = entity_response.json()

    document_response = client.post(
        f"/api/v1/entities/{entity['id']}/documents",
        files={
            "file": (
                "processing-job-test.txt",
                BytesIO(b"Processing job test content"),
                "text/plain",
            )
        },
    )
    assert document_response.status_code == 201
    return document_response.json()


def test_create_processing_job():
    document = create_document()

    response = client.post(
        "/api/v1/processing-jobs",
        json={
            "document_id": document["id"],
            "job_type": "extract_text",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["document_id"] == document["id"]
    assert data["job_type"] == "extract_text"
    assert data["status"] == "pending"
    assert data["progress"] == 0


def test_list_processing_jobs():
    response = client.get("/api/v1/processing-jobs")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_document_processing_jobs():
    document = create_document()

    create_response = client.post(
        "/api/v1/processing-jobs",
        json={
            "document_id": document["id"],
            "job_type": "extract_text",
        },
    )
    assert create_response.status_code == 201

    response = client.get(f"/api/v1/documents/{document['id']}/processing-jobs")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
