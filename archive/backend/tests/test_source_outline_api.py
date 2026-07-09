from fastapi.testclient import TestClient

import app.api.source_outline as source_outline_api
from app.connectors.repository import SourceOutlineFile, SourceOutlinePreview, SourceOutlineSymbol
from app.main import app

client = TestClient(app)


class FakeSourceOutlineBuilder:
    def __init__(self, preview=None, error=None):
        self.preview = preview
        self.error = error
        self.repository_path = None

    def build(self, repository_path):
        self.repository_path = repository_path

        if self.error:
            raise self.error

        return self.preview


def test_source_outline_api_returns_preview(monkeypatch):
    builder = FakeSourceOutlineBuilder(
        SourceOutlinePreview(
            files=[
                SourceOutlineFile(
                    "main.py",
                    ".py",
                    "Python",
                    [SourceOutlineSymbol("run", "function", 1)],
                )
            ]
        )
    )

    monkeypatch.setattr(source_outline_api, "SourceOutlinePreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-source-outline",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["symbol_count"] == 1
    assert response.json()["files"][0]["symbols"][0]["name"] == "run"
    assert builder.repository_path == "/repo"


def test_source_outline_api_returns_empty_preview(monkeypatch):
    builder = FakeSourceOutlineBuilder(SourceOutlinePreview())

    monkeypatch.setattr(source_outline_api, "SourceOutlinePreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-source-outline",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["outcome"] == "no_source_files"


def test_source_outline_api_rejects_empty_path():
    response = client.post(
        "/api/v1/repository-source-outline",
        json={"repository_path": ""},
    )

    assert response.status_code == 422


def test_source_outline_api_maps_file_not_found_to_400(monkeypatch):
    builder = FakeSourceOutlineBuilder(error=FileNotFoundError("missing repo"))

    monkeypatch.setattr(source_outline_api, "SourceOutlinePreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-source-outline",
        json={"repository_path": "/missing"},
    )

    assert response.status_code == 400
    assert "missing repo" in response.json()["detail"]


def test_source_outline_api_maps_value_error_to_400(monkeypatch):
    builder = FakeSourceOutlineBuilder(error=ValueError("bad repo"))

    monkeypatch.setattr(source_outline_api, "SourceOutlinePreviewBuilder", lambda: builder)

    response = client.post(
        "/api/v1/repository-source-outline",
        json={"repository_path": "/repo"},
    )

    assert response.status_code == 400
    assert "bad repo" in response.json()["detail"]
