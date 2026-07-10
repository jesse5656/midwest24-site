from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_structure import serialize_repository_structure_report
from app.connectors.repository.repository_structure import (
    RepositoryStructureBuilder,
    RepositoryStructureNode,
    RepositoryStructureReport,
)
from app.connectors.repository.repository_structure_summary import RepositoryStructureSummaryBuilder
from app.main import app

client = TestClient(app)


def make_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")
    (repo / "app").mkdir()
    (repo / "app" / "main.py").write_text("def run():\n    pass\n", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "HEAD").write_text("ignore\n", encoding="utf-8")
    return repo


def test_repository_structure_001_node_count_manual():
    report = RepositoryStructureReport(
        repository_path="/repo",
        nodes=[
            RepositoryStructureNode("README.md", "file", 1),
            RepositoryStructureNode("app", "directory", 1, 1),
        ],
    )
    assert report.node_count == 2


def test_repository_structure_002_file_count_manual():
    report = RepositoryStructureReport(
        repository_path="/repo",
        nodes=[
            RepositoryStructureNode("README.md", "file", 1),
            RepositoryStructureNode("app", "directory", 1, 1),
        ],
    )
    assert report.file_count == 1


def test_repository_structure_003_directory_count_manual():
    report = RepositoryStructureReport(
        repository_path="/repo",
        nodes=[
            RepositoryStructureNode("README.md", "file", 1),
            RepositoryStructureNode("app", "directory", 1, 1),
        ],
    )
    assert report.directory_count == 1


def test_repository_structure_004_max_depth_manual():
    report = RepositoryStructureReport(
        repository_path="/repo",
        nodes=[
            RepositoryStructureNode("README.md", "file", 1),
            RepositoryStructureNode("app/main.py", "file", 2),
        ],
    )
    assert report.max_depth == 2


def test_repository_structure_005_top_level_nodes_manual():
    report = RepositoryStructureReport(
        repository_path="/repo",
        nodes=[
            RepositoryStructureNode("README.md", "file", 1),
            RepositoryStructureNode("app/main.py", "file", 2),
        ],
    )
    assert [node.path for node in report.top_level_nodes] == ["README.md"]


def test_repository_structure_006_empty_max_depth_zero():
    assert RepositoryStructureReport("/repo").max_depth == 0


def test_repository_structure_007_builder_finds_files(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositoryStructureBuilder().build(repo)
    assert "README.md" in [node.path for node in report.nodes]


def test_repository_structure_008_builder_finds_directories(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositoryStructureBuilder().build(repo)
    assert "app" in [node.path for node in report.nodes]


def test_repository_structure_009_builder_finds_nested_file(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositoryStructureBuilder().build(repo)
    assert "app/main.py" in [node.path for node in report.nodes]


def test_repository_structure_010_builder_ignores_git(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositoryStructureBuilder().build(repo)
    assert ".git/HEAD" not in [node.path for node in report.nodes]


def test_repository_structure_011_builder_respects_max_depth(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositoryStructureBuilder().build(repo, max_depth=1)
    assert "app/main.py" not in [node.path for node in report.nodes]


def test_repository_structure_012_builder_records_child_count(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositoryStructureBuilder().build(repo)
    app_node = next(node for node in report.nodes if node.path == "app")
    assert app_node.child_count == 1


def test_repository_structure_013_builder_missing_path_raises(tmp_path):
    missing = tmp_path / "missing"
    try:
        RepositoryStructureBuilder().build(missing)
        assert False
    except FileNotFoundError:
        assert True


def test_repository_structure_014_builder_file_path_raises(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")
    try:
        RepositoryStructureBuilder().build(file_path)
        assert False
    except NotADirectoryError:
        assert True


def test_repository_structure_015_summary_empty():
    summary = RepositoryStructureSummaryBuilder().build(RepositoryStructureReport("/repo"))
    assert summary.outcome == "empty_repository"


def test_repository_structure_016_summary_detected():
    report = RepositoryStructureReport(
        "/repo",
        [RepositoryStructureNode("README.md", "file", 1)],
    )
    summary = RepositoryStructureSummaryBuilder().build(report)
    assert summary.outcome == "structure_detected"


def test_repository_structure_017_summary_no_action():
    report = RepositoryStructureReport(
        "/repo",
        [RepositoryStructureNode("README.md", "file", 1)],
    )
    summary = RepositoryStructureSummaryBuilder().build(report)
    assert summary.action_required is False


def test_repository_structure_018_summary_mentions_files():
    report = RepositoryStructureReport(
        "/repo",
        [RepositoryStructureNode("README.md", "file", 1)],
    )
    summary = RepositoryStructureSummaryBuilder().build(report)
    assert "file" in summary.message


def test_repository_structure_019_serialize_counts():
    report = RepositoryStructureReport(
        "/repo",
        [RepositoryStructureNode("README.md", "file", 1)],
    )
    response = serialize_repository_structure_report(report)
    assert response.node_count == 1
    assert response.file_count == 1


def test_repository_structure_020_serialize_summary():
    report = RepositoryStructureReport(
        "/repo",
        [RepositoryStructureNode("README.md", "file", 1)],
    )
    response = serialize_repository_structure_report(report)
    assert response.summary.outcome == "structure_detected"


def test_repository_structure_021_api_returns_200(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post(
        "/api/v1/repository-structure",
        json={"repository_path": str(repo)},
    )
    assert response.status_code == 200


def test_repository_structure_022_api_returns_file_count(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post(
        "/api/v1/repository-structure",
        json={"repository_path": str(repo)},
    )
    assert response.json()["file_count"] >= 2


def test_repository_structure_023_api_returns_directory_count(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post(
        "/api/v1/repository-structure",
        json={"repository_path": str(repo)},
    )
    assert response.json()["directory_count"] >= 1


def test_repository_structure_024_api_returns_summary(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post(
        "/api/v1/repository-structure",
        json={"repository_path": str(repo)},
    )
    assert response.json()["summary"]["outcome"] == "structure_detected"


def test_repository_structure_025_api_respects_depth(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post(
        "/api/v1/repository-structure",
        json={"repository_path": str(repo), "max_depth": 1},
    )
    paths = [node["path"] for node in response.json()["nodes"]]
    assert "app/main.py" not in paths


def test_repository_structure_026_api_rejects_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-structure",
        json={"repository_path": str(tmp_path / "missing")},
    )
    assert response.status_code == 400


def test_repository_structure_027_api_rejects_empty_path():
    response = client.post(
        "/api/v1/repository-structure",
        json={"repository_path": ""},
    )
    assert response.status_code == 422


def test_repository_structure_028_api_rejects_zero_depth(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post(
        "/api/v1/repository-structure",
        json={"repository_path": str(repo), "max_depth": 0},
    )
    assert response.status_code == 422


def test_repository_structure_029_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-structure" in paths


def test_repository_structure_030_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/repository-structure")
    assert "POST" in route.methods
