from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_knowledge_graph import serialize_repository_knowledge_graph
from app.connectors.repository.repository_knowledge_graph import (
    RepositoryKnowledgeGraph,
    RepositoryKnowledgeGraphBuilder,
    RepositoryKnowledgeGraphEdge,
    RepositoryKnowledgeGraphNode,
)
from app.connectors.repository.repository_knowledge_graph_summary import RepositoryKnowledgeGraphSummaryBuilder
from app.main import app

client = TestClient(app)


def make_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "requirements.txt").write_text("fastapi\n", encoding="utf-8")
    (repo / "app.py").write_text(
        "import os\n"
        "MAX_SIZE = 10\n"
        "class Worker:\n"
        "    def run(self):\n"
        "        return os.getcwd()\n",
        encoding="utf-8",
    )
    return repo


def test_knowledge_graph_001_manual_node_count():
    graph = RepositoryKnowledgeGraph(
        "/repo",
        [RepositoryKnowledgeGraphNode("repository:root", "repository", "repo", "/repo")],
        [],
    )
    assert graph.node_count == 1


def test_knowledge_graph_002_manual_edge_count():
    graph = RepositoryKnowledgeGraph(
        "/repo",
        [],
        [RepositoryKnowledgeGraphEdge("a", "b", "relates")],
    )
    assert graph.edge_count == 1


def test_knowledge_graph_003_node_types():
    graph = RepositoryKnowledgeGraph(
        "/repo",
        [
            RepositoryKnowledgeGraphNode("repository:root", "repository", "repo", "/repo"),
            RepositoryKnowledgeGraphNode("file:a.py", "file", "a.py", "a.py"),
        ],
        [],
    )
    assert graph.node_types == ["file", "repository"]


def test_knowledge_graph_004_relationship_types():
    graph = RepositoryKnowledgeGraph(
        "/repo",
        [],
        [RepositoryKnowledgeGraphEdge("repository:root", "file:a.py", "contains_file")],
    )
    assert graph.relationship_types == ["contains_file"]


def test_knowledge_graph_005_builder_has_repository_node(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    assert "repository:root" in [node.node_id for node in graph.nodes]


def test_knowledge_graph_006_builder_has_file_nodes(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    assert graph.file_node_count >= 2


def test_knowledge_graph_007_builder_has_dependency_node(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    assert "dependency:python:fastapi" in [node.node_id for node in graph.nodes]


def test_knowledge_graph_008_builder_has_import_node(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    assert "import:os" in [node.node_id for node in graph.nodes]


def test_knowledge_graph_009_builder_has_symbol_node(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    assert "symbol:app.py:Worker" in [node.node_id for node in graph.nodes]


def test_knowledge_graph_010_builder_has_contains_edges(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    assert "contains_file" in graph.relationship_types


def test_knowledge_graph_011_builder_has_dependency_edges(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    assert "declares_dependency" in graph.relationship_types


def test_knowledge_graph_012_builder_has_import_edges(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    assert "imports" in graph.relationship_types


def test_knowledge_graph_013_builder_has_symbol_edges(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    assert "defines_symbol" in graph.relationship_types


def test_knowledge_graph_014_builder_missing_path_raises(tmp_path):
    try:
        RepositoryKnowledgeGraphBuilder().build(tmp_path / "missing")
        assert False
    except FileNotFoundError:
        assert True


def test_knowledge_graph_015_builder_file_path_raises(tmp_path):
    path = tmp_path / "file.py"
    path.write_text("x", encoding="utf-8")
    try:
        RepositoryKnowledgeGraphBuilder().build(path)
        assert False
    except NotADirectoryError:
        assert True


def test_knowledge_graph_016_summary_empty():
    summary = RepositoryKnowledgeGraphSummaryBuilder().build(RepositoryKnowledgeGraph("/repo"))
    assert summary.outcome == "empty_graph"


def test_knowledge_graph_017_summary_built(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    summary = RepositoryKnowledgeGraphSummaryBuilder().build(graph)
    assert summary.outcome == "graph_built"


def test_knowledge_graph_018_summary_no_action(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    summary = RepositoryKnowledgeGraphSummaryBuilder().build(graph)
    assert summary.action_required is False


def test_knowledge_graph_019_serialize_counts(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    response = serialize_repository_knowledge_graph(graph)
    assert response.node_count == graph.node_count
    assert response.edge_count == graph.edge_count


def test_knowledge_graph_020_serialize_summary(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    response = serialize_repository_knowledge_graph(graph)
    assert response.summary.outcome == "graph_built"


def test_knowledge_graph_021_api_returns_200(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-knowledge-graph", json={"repository_path": str(repo)})
    assert response.status_code == 200


def test_knowledge_graph_022_api_returns_node_count(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-knowledge-graph", json={"repository_path": str(repo)})
    assert response.json()["node_count"] > 0


def test_knowledge_graph_023_api_returns_edge_count(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-knowledge-graph", json={"repository_path": str(repo)})
    assert response.json()["edge_count"] > 0


def test_knowledge_graph_024_api_returns_node_types(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-knowledge-graph", json={"repository_path": str(repo)})
    assert "repository" in response.json()["node_types"]
    assert "file" in response.json()["node_types"]


def test_knowledge_graph_025_api_returns_relationship_types(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-knowledge-graph", json={"repository_path": str(repo)})
    assert "contains_file" in response.json()["relationship_types"]


def test_knowledge_graph_026_api_rejects_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-knowledge-graph",
        json={"repository_path": str(tmp_path / "missing")},
    )
    assert response.status_code == 400


def test_knowledge_graph_027_api_rejects_empty_path():
    response = client.post("/api/v1/repository-knowledge-graph", json={"repository_path": ""})
    assert response.status_code == 422


def test_knowledge_graph_028_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-knowledge-graph" in paths


def test_knowledge_graph_029_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/repository-knowledge-graph")
    assert "POST" in route.methods


def test_knowledge_graph_030_nodes_by_type(tmp_path):
    repo = make_repo(tmp_path)
    graph = RepositoryKnowledgeGraphBuilder().build(repo)
    assert graph.nodes_by_type("repository")[0].node_id == "repository:root"
