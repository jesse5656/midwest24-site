from fastapi.testclient import TestClient

import app.api.code_inventory as code_inventory_api
from app.connectors.repository import CodeInventoryFile, CodeInventoryPreview
from app.main import app

client = TestClient(app)


class FakeCodeInventoryBuilder:
    def __init__(self, preview=None, error=None):
        self.preview = preview
        self.error = error
        self.repository_path = None

    def build(self, repository_path):
        self.repository_path = repository_path

        if self.error:
            raise self.error

        return self.preview


def test_code_inventory_api_returns_preview(monkeypatch):
    builder = FakeCodeInventoryBuilder(
        CodeInventoryPreview(
            files=[CodeInventoryFile("main.py", ".py", "Python", 10)]
        )
    )

    monkeypatch.setattr(code_inventory_api, "CodeInventoryPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-code-inventory",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["file_count"] == 1
    assert response.json()["files"][0]["language"] == "Python"
    assert builder.repository_path == "/repo"


def test_code_inventory_api_returns_empty_preview(monkeypatch):
    builder = FakeCodeInventoryBuilder(CodeInventoryPreview())

    monkeypatch.setattr(code_inventory_api, "CodeInventoryPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-code-inventory",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["outcome"] == "empty_inventory"


def test_code_inventory_api_rejects_empty_path():
    response = client.post(
        "/api/v1/repository-code-inventory",
        json={"repository_path": ""},
    )

    assert response.status_code == 422


def test_code_inventory_api_maps_file_not_found_to_400(monkeypatch):
    builder = FakeCodeInventoryBuilder(error=FileNotFoundError("missing repo"))

    monkeypatch.setattr(code_inventory_api, "CodeInventoryPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-code-inventory",
        json={"repository_path": "/missing"},
    )

    assert response.status_code == 400
    assert "missing repo" in response.json()["detail"]


def test_code_inventory_api_maps_value_error_to_400(monkeypatch):
    builder = FakeCodeInventoryBuilder(error=ValueError("bad repo"))

    monkeypatch.setattr(code_inventory_api, "CodeInventoryPreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-code-inventory",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "bad repo" in response.json()["detail"]
