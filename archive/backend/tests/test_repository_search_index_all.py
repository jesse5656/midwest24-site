from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_search_index import (
    serialize_repository_search_index,
)
from app.connectors.repository.repository_search_index import (
    RepositorySearchDocument,
    RepositorySearchIndex,
    RepositorySearchIndexBuilder,
)
from app.connectors.repository.repository_search_index_summary import (
    RepositorySearchIndexSummaryBuilder,
)
from app.main import app

client = TestClient(app)


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "requirements.txt").write_text(
        "fastapi\n",
        encoding="utf-8",
    )

    (repo / "app.py").write_text(
        "import os\n"
        "class Worker:\n"
        "    def run(self):\n"
        "        return os.getcwd()\n",
        encoding="utf-8",
    )

    return repo


def test_search_index_001_searchable_text():
    document = RepositorySearchDocument(
        "1",
        "symbol",
        "Worker",
        "Python service",
        "app.py",
    )
    assert "worker" in document.searchable_text


def test_search_index_002_document_count():
    index = RepositorySearchIndex(
        "/repo",
        [
            RepositorySearchDocument(
                "1",
                "file",
                "app.py",
                "body",
                "app.py",
            )
        ],
    )
    assert index.document_count == 1


def test_search_index_003_document_types():
    index = RepositorySearchIndex(
        "/repo",
        [
            RepositorySearchDocument(
                "1",
                "file",
                "app.py",
                "body",
                "app.py",
            ),
            RepositorySearchDocument(
                "2",
                "symbol",
                "Worker",
                "body",
                "app.py",
            ),
        ],
    )
    assert index.document_types == ["file", "symbol"]


def test_search_index_004_empty_search():
    index = RepositorySearchIndex("/repo", [])
    assert index.search("") == []


def test_search_index_005_search_title():
    index = RepositorySearchIndex(
        "/repo",
        [
            RepositorySearchDocument(
                "1",
                "symbol",
                "Worker",
                "body",
                "app.py",
            )
        ],
    )
    assert index.search("worker")[0].title == "Worker"


def test_search_index_006_search_body():
    index = RepositorySearchIndex(
        "/repo",
        [
            RepositorySearchDocument(
                "1",
                "dependency",
                "fastapi",
                "python dependency",
                "requirements.txt",
            )
        ],
    )
    assert index.search("dependency")[0].document_id == "1"


def test_search_index_007_search_limit():
    index = RepositorySearchIndex(
        "/repo",
        [
            RepositorySearchDocument(
                "1",
                "file",
                "app",
                "python",
                "app.py",
            ),
            RepositorySearchDocument(
                "2",
                "file",
                "other",
                "python",
                "other.py",
            ),
        ],
    )
    assert len(index.search("python", limit=1)) == 1


def test_search_index_008_builder_documents(tmp_path):
    index = RepositorySearchIndexBuilder().build(make_repo(tmp_path))
    assert index.document_count > 0


def test_search_index_009_builder_file_type(tmp_path):
    index = RepositorySearchIndexBuilder().build(make_repo(tmp_path))
    assert "file" in index.document_types


def test_search_index_010_builder_symbol_type(tmp_path):
    index = RepositorySearchIndexBuilder().build(make_repo(tmp_path))
    assert "symbol" in index.document_types


def test_search_index_011_builder_dependency_type(tmp_path):
    index = RepositorySearchIndexBuilder().build(make_repo(tmp_path))
    assert "dependency" in index.document_types


def test_search_index_012_builder_relationship_type(tmp_path):
    index = RepositorySearchIndexBuilder().build(make_repo(tmp_path))
    assert "relationship" in index.document_types


def test_search_index_013_builder_search_worker(tmp_path):
    index = RepositorySearchIndexBuilder().build(make_repo(tmp_path))
    assert index.search("worker")


def test_search_index_014_builder_search_fastapi(tmp_path):
    index = RepositorySearchIndexBuilder().build(make_repo(tmp_path))
    assert index.search("fastapi")


def test_search_index_015_missing_path(tmp_path):
    try:
        RepositorySearchIndexBuilder().build(tmp_path / "missing")
        assert False
    except FileNotFoundError:
        assert True


def test_search_index_016_file_path(tmp_path):
    file_path = tmp_path / "file.py"
    file_path.write_text("x", encoding="utf-8")

    try:
        RepositorySearchIndexBuilder().build(file_path)
        assert False
    except NotADirectoryError:
        assert True


def test_search_index_017_summary_empty():
    summary = RepositorySearchIndexSummaryBuilder().build(
        RepositorySearchIndex("/repo", [])
    )
    assert summary.outcome == "empty_index"


def test_search_index_018_summary_built():
    summary = RepositorySearchIndexSummaryBuilder().build(
        RepositorySearchIndex(
            "/repo",
            [
                RepositorySearchDocument(
                    "1",
                    "file",
                    "app.py",
                    "body",
                    "app.py",
                )
            ],
        )
    )
    assert summary.outcome == "index_built"


def test_search_index_019_serialize():
    response = serialize_repository_search_index(
        RepositorySearchIndex(
            "/repo",
            [
                RepositorySearchDocument(
                    "1",
                    "file",
                    "app.py",
                    "python",
                    "app.py",
                )
            ],
        ),
        query="python",
    )
    assert response.result_count == 1


def test_search_index_020_api_200(tmp_path):
    response = client.post(
        "/api/v1/repository-search-index",
        json={
            "repository_path": str(make_repo(tmp_path)),
        },
    )
    assert response.status_code == 200


def test_search_index_021_api_documents(tmp_path):
    response = client.post(
        "/api/v1/repository-search-index",
        json={
            "repository_path": str(make_repo(tmp_path)),
        },
    )
    assert response.json()["document_count"] > 0


def test_search_index_022_api_results(tmp_path):
    response = client.post(
        "/api/v1/repository-search-index",
        json={
            "repository_path": str(make_repo(tmp_path)),
            "query": "worker",
        },
    )
    assert response.json()["result_count"] > 0


def test_search_index_023_api_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-search-index",
        json={
            "repository_path": str(tmp_path / "missing"),
        },
    )
    assert response.status_code == 400


def test_search_index_024_api_empty_path():
    response = client.post(
        "/api/v1/repository-search-index",
        json={
            "repository_path": "",
        },
    )
    assert response.status_code == 422


def test_search_index_025_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-search-index" in paths


def test_search_index_026_route_post():
    route = next(
        route
        for route in app.routes
        if route.path == "/api/v1/repository-search-index"
    )
    assert "POST" in route.methods
