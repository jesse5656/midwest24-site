from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_cross_reference_graph import serialize_repository_cross_reference_graph
from app.connectors.repository.repository_cross_reference_graph import (
    RepositoryCrossReference,
    RepositoryCrossReferenceGraph,
    RepositoryCrossReferenceGraphBuilder,
)
from app.connectors.repository.repository_cross_reference_graph_summary import (
    RepositoryCrossReferenceGraphSummaryBuilder,
)
from app.main import app

client = TestClient(app)


def make_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app").mkdir()
    (repo / "app" / "main.py").write_text(
        "class Worker:\n"
        "    def run(self):\n"
        "        helper()\n"
        "        self.service.execute()\n"
        "def helper():\n"
        "    value = len([1, 2, 3])\n"
        "    return value\n",
        encoding="utf-8",
    )
    (repo / "app" / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "ignored.py").write_text("ignored()\n", encoding="utf-8")
    return repo


def test_cross_reference_001_manual_reference_count():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [RepositoryCrossReference("a.py", "f", "helper", "call", 1)],
    )
    assert graph.reference_count == 1


def test_cross_reference_002_manual_source_files():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [RepositoryCrossReference("a.py", "f", "helper", "call", 1)],
    )
    assert graph.source_files == ["a.py"]


def test_cross_reference_003_manual_referenced_names():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [RepositoryCrossReference("a.py", "f", "helper", "call", 1)],
    )
    assert graph.referenced_names == ["helper"]


def test_cross_reference_004_call_count():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [RepositoryCrossReference("a.py", "f", "helper", "call", 1)],
    )
    assert graph.call_count == 1


def test_cross_reference_005_attribute_count():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [RepositoryCrossReference("a.py", "f", "self.service", "attribute", 1)],
    )
    assert graph.attribute_count == 1


def test_cross_reference_006_name_count():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [RepositoryCrossReference("a.py", "f", "value", "name", 1)],
    )
    assert graph.name_count == 1


def test_cross_reference_007_references_for_file():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [
            RepositoryCrossReference("a.py", "f", "helper", "call", 1),
            RepositoryCrossReference("b.py", "g", "other", "call", 1),
        ],
    )
    assert [reference.referenced_name for reference in graph.references_for_file("a.py")] == ["helper"]


def test_cross_reference_008_references_to_name():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [
            RepositoryCrossReference("a.py", "f", "helper", "call", 1),
            RepositoryCrossReference("b.py", "g", "helper", "call", 1),
        ],
    )
    assert len(graph.references_to_name("helper")) == 2


def test_cross_reference_009_builder_detects_helper_call(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryCrossReferenceGraphBuilder().build(repo)
    assert "helper" in graph.referenced_names


def test_cross_reference_010_builder_detects_len_call(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryCrossReferenceGraphBuilder().build(repo)
    assert "len" in graph.referenced_names


def test_cross_reference_011_builder_detects_attribute(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryCrossReferenceGraphBuilder().build(repo)
    assert "self.service.execute" in graph.referenced_names


def test_cross_reference_012_builder_records_source_symbol(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryCrossReferenceGraphBuilder().build(repo)
    call = [reference for reference in graph.references if reference.referenced_name == "helper"][0]
    assert call.source_symbol == "Worker.run"


def test_cross_reference_013_builder_ignores_git(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryCrossReferenceGraphBuilder().build(repo)
    assert "ignored" not in graph.referenced_names


def test_cross_reference_014_builder_ignores_syntax_errors(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryCrossReferenceGraphBuilder().build(repo)
    assert "app/broken.py" not in graph.source_files


def test_cross_reference_015_builder_has_references(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryCrossReferenceGraphBuilder().build(repo)
    assert graph.reference_count > 0


def test_cross_reference_016_builder_source_file_count(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryCrossReferenceGraphBuilder().build(repo)
    assert graph.source_file_count == 1


def test_cross_reference_017_builder_respects_depth(tmp_path):
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "main.py").write_text("helper()\n", encoding="utf-8")
    graph = RepositoryCrossReferenceGraphBuilder().build(repo, max_depth=1)
    assert graph.reference_count == 0


def test_cross_reference_018_builder_missing_path_raises(tmp_path):
    try:
        RepositoryCrossReferenceGraphBuilder().build(tmp_path / "missing")
        assert False
    except FileNotFoundError:
        assert True


def test_cross_reference_019_builder_file_path_raises(tmp_path):
    path = tmp_path / "file.py"
    path.write_text("helper()\n", encoding="utf-8")
    try:
        RepositoryCrossReferenceGraphBuilder().build(path)
        assert False
    except NotADirectoryError:
        assert True


def test_cross_reference_020_summary_no_references():
    summary = RepositoryCrossReferenceGraphSummaryBuilder().build(RepositoryCrossReferenceGraph("/repo"))
    assert summary.outcome == "no_references"


def test_cross_reference_021_summary_detected():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [RepositoryCrossReference("a.py", "f", "helper", "call", 1)],
    )
    summary = RepositoryCrossReferenceGraphSummaryBuilder().build(graph)
    assert summary.outcome == "references_detected"


def test_cross_reference_022_summary_no_action():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [RepositoryCrossReference("a.py", "f", "helper", "call", 1)],
    )
    summary = RepositoryCrossReferenceGraphSummaryBuilder().build(graph)
    assert summary.action_required is False


def test_cross_reference_023_summary_mentions_references():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [RepositoryCrossReference("a.py", "f", "helper", "call", 1)],
    )
    summary = RepositoryCrossReferenceGraphSummaryBuilder().build(graph)
    assert "1 reference" in summary.message


def test_cross_reference_024_serialize_counts():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [RepositoryCrossReference("a.py", "f", "helper", "call", 1)],
    )
    response = serialize_repository_cross_reference_graph(graph)
    assert response.reference_count == 1
    assert response.call_count == 1


def test_cross_reference_025_serialize_summary():
    graph = RepositoryCrossReferenceGraph(
        "/repo",
        [RepositoryCrossReference("a.py", "f", "helper", "call", 1)],
    )
    response = serialize_repository_cross_reference_graph(graph)
    assert response.summary.outcome == "references_detected"


def test_cross_reference_026_api_returns_200(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-cross-reference-graph", json={"repository_path": str(repo)})
    assert response.status_code == 200


def test_cross_reference_027_api_returns_reference_count(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-cross-reference-graph", json={"repository_path": str(repo)})
    assert response.json()["reference_count"] > 0


def test_cross_reference_028_api_returns_referenced_names(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-cross-reference-graph", json={"repository_path": str(repo)})
    assert "helper" in response.json()["referenced_names"]


def test_cross_reference_029_api_returns_source_files(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-cross-reference-graph", json={"repository_path": str(repo)})
    assert response.json()["source_files"] == ["app/main.py"]


def test_cross_reference_030_api_respects_depth(tmp_path):
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "main.py").write_text("helper()\n", encoding="utf-8")
    response = client.post(
        "/api/v1/repository-cross-reference-graph",
        json={"repository_path": str(repo), "max_depth": 1},
    )
    assert response.json()["reference_count"] == 0


def test_cross_reference_031_api_rejects_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-cross-reference-graph",
        json={"repository_path": str(tmp_path / "missing")},
    )
    assert response.status_code == 400


def test_cross_reference_032_api_rejects_empty_path():
    response = client.post("/api/v1/repository-cross-reference-graph", json={"repository_path": ""})
    assert response.status_code == 422


def test_cross_reference_033_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-cross-reference-graph" in paths


def test_cross_reference_034_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/repository-cross-reference-graph")
    assert "POST" in route.methods
