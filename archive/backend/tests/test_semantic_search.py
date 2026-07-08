from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_semantic_search_endpoint():
    entity = client.post(
        "/api/v1/entities",
        json={
            "entity_type": "document",
            "title": "Semantic Search Test",
        },
    ).json()

    document = client.post(
        f"/api/v1/entities/{entity['id']}/documents",
        files={
            "file": (
                "semantic.txt",
                BytesIO(
                    b"Storm damage inspection procedures.\n\nRoof replacement planning."
                ),
                "text/plain",
            )
        },
    ).json()

    job = client.post(
        "/api/v1/processing-jobs",
        json={
            "document_id": document["id"],
            "job_type": "extract_text",
        },
    )

    assert job.status_code == 201

    response = client.post(
        "/api/v1/search/semantic",
        json={
            "query": "storm inspection",
            "limit": 5,
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
