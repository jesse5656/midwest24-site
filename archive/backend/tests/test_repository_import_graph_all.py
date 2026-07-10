from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_import_graph import serialize_repository_import_graph
from app.connectors.repository.repository_import_graph import (
    RepositoryImportEdge,
    RepositoryImportGraph,
    RepositoryImportGraphBuilder,
)
from app.connectors.repository.repository_import_graph_summary import RepositoryImportGraphSummaryBuilder
from app.main import app

client = TestClient(app)


def make_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app").mkdir()
    (repo / "app" / "main.py").write_text(
        "import os\nimport sys as system\nfrom pathlib import Path\nfrom .services import worker\n",
        encoding="utf-8",
    )
    (repo / "app" / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "ignored.py").write_text("import ignored\n", encoding="utf-8")
    return repo


def test_import_graph_001_manual_edge_count():
    graph = RepositoryImportGraph("/repo", [RepositoryImportEdge("a.py", "os", "import", 1)])
    assert graph.edge_count == 1


def test_import_graph_002_manual_source_files():
    graph = RepositoryImportGraph("/repo", [RepositoryImportEdge("a.py", "os", "import", 1)])
    assert graph.source_files == ["a.py"]


def test_import_graph_003_manual_imported_names():
    graph = RepositoryImportGraph("/repo", [RepositoryImportEdge("a.py", "os", "import", 1)])
    assert graph.imported_names == ["os"]


def test_import_graph_004_edges_for_source():
    graph = RepositoryImportGraph(
        "/repo",
        [
            RepositoryImportEdge("a.py", "os", "import", 1),
            RepositoryImportEdge("b.py", "sys", "import", 1),
        ],
    )
    assert [edge.imported_name for edge in graph.edges_for_source("a.py")] == ["os"]


def test_import_graph_005_builder_finds_import(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryImportGraphBuilder().build(repo)
    assert "os" in graph.imported_names


def test_import_graph_006_builder_finds_import_alias_original_name(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryImportGraphBuilder().build(repo)
    assert "sys" in graph.imported_names


def test_import_graph_007_builder_finds_from_import(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryImportGraphBuilder().build(repo)
    assert "pathlib.Path" in graph.imported_names


def test_import_graph_008_builder_finds_relative_import(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryImportGraphBuilder().build(repo)
    assert ".services.worker" in graph.imported_names


def test_import_graph_009_builder_ignores_git(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryImportGraphBuilder().build(repo)
    assert "ignored" not in graph.imported_names


def test_import_graph_010_builder_ignores_syntax_errors(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryImportGraphBuilder().build(repo)
    assert "app/broken.py" not in graph.source_files


def test_import_graph_011_builder_edge_count(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryImportGraphBuilder().build(repo)
    assert graph.edge_count == 4


def test_import_graph_012_builder_source_file_count(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryImportGraphBuilder().build(repo)
    assert graph.source_file_count == 1


def test_import_graph_013_builder_imported_name_count(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryImportGraphBuilder().build(repo)
    assert graph.imported_name_count == 4


def test_import_graph_014_builder_respects_depth(tmp_path):
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "main.py").write_text("import os\n", encoding="utf-8")
    graph = RepositoryImportGraphBuilder().build(repo, max_depth=1)
    assert graph.edge_count == 0


def test_import_graph_015_builder_missing_path_raises(tmp_path):
    try:
        RepositoryImportGraphBuilder().build(tmp_path / "missing")
        assert False
    except FileNotFoundError:
        assert True


def test_import_graph_016_builder_file_path_raises(tmp_path):
    path = tmp_path / "file.py"
    path.write_text("import os\n", encoding="utf-8")
    try:
        RepositoryImportGraphBuilder().build(path)
        assert False
    except NotADirectoryError:
        assert True


def test_import_graph_017_summary_no_imports():
    summary = RepositoryImportGraphSummaryBuilder().build(RepositoryImportGraph("/repo"))
    assert summary.outcome == "no_imports"


def test_import_graph_018_summary_detected():
    graph = RepositoryImportGraph("/repo", [RepositoryImportEdge("a.py", "os", "import", 1)])
    summary = RepositoryImportGraphSummaryBuilder().build(graph)
    assert summary.outcome == "imports_detected"


def test_import_graph_019_summary_no_action():
    graph = RepositoryImportGraph("/repo", [RepositoryImportEdge("a.py", "os", "import", 1)])
    summary = RepositoryImportGraphSummaryBuilder().build(graph)
    assert summary.action_required is False


def test_import_graph_020_summary_mentions_edges():
    graph = RepositoryImportGraph("/repo", [RepositoryImportEdge("a.py", "os", "import", 1)])
    summary = RepositoryImportGraphSummaryBuilder().build(graph)
    assert "1 import edge" in summary.message


def test_import_graph_021_serialize_counts():
    graph = RepositoryImportGraph("/repo", [RepositoryImportEdge("a.py", "os", "import", 1)])
    response = serialize_repository_import_graph(graph)
    assert response.edge_count == 1
    assert response.source_file_count == 1


def test_import_graph_022_serialize_summary():
    graph = RepositoryImportGraph("/repo", [RepositoryImportEdge("a.py", "os", "import", 1)])
    response = serialize_repository_import_graph(graph)
    assert response.summary.outcome == "imports_detected"


def test_import_graph_023_api_returns_200(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-import-graph", json={"repository_path": str(repo)})
    assert response.status_code == 200


def test_import_graph_024_api_returns_edge_count(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-import-graph", json={"repository_path": str(repo)})
    assert response.json()["edge_count"] == 4


def test_import_graph_025_api_returns_imported_names(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-import-graph", json={"repository_path": str(repo)})
    assert "os" in response.json()["imported_names"]


def test_import_graph_026_api_returns_source_files(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-import-graph", json={"repository_path": str(repo)})
    assert response.json()["source_files"] == ["app/main.py"]


def test_import_graph_027_api_respects_depth(tmp_path):
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "main.py").write_text("import os\n", encoding="utf-8")
    response = client.post(
        "/api/v1/repository-import-graph",
        json={"repository_path": str(repo), "max_depth": 1},
    )
    assert response.json()["edge_count"] == 0


def test_import_graph_028_api_rejects_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-import-graph",
        json={"repository_path": str(tmp_path / "missing")},
    )
    assert response.status_code == 400


def test_import_graph_029_api_rejects_empty_path():
    response = client.post("/api/v1/repository-import-graph", json={"repository_path": ""})
    assert response.status_code == 422


def test_import_graph_030_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-import-graph" in paths


def test_import_graph_031_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/repository-import-graph")
    assert "POST" in route.methods
