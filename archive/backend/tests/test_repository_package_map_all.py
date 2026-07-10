from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_package_map import serialize_repository_package_map
from app.connectors.repository.repository_package_map import (
    PACKAGE_MARKERS,
    RepositoryPackageMap,
    RepositoryPackageMapBuilder,
    RepositoryPackageMarker,
)
from app.connectors.repository.repository_package_map_summary import RepositoryPackageMapSummaryBuilder
from app.main import app

client = TestClient(app)


def make_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (repo / "package.json").write_text('{"name":"x"}\n', encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "requirements.txt").write_text("fastapi\n", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "package.json").write_text("{}\n", encoding="utf-8")
    return repo


def test_repository_package_map_001_known_python_marker():
    assert PACKAGE_MARKERS["pyproject.toml"] == "python"


def test_repository_package_map_002_known_node_marker():
    assert PACKAGE_MARKERS["package.json"] == "node"


def test_repository_package_map_003_marker_count_manual():
    package_map = RepositoryPackageMap(
        "/repo",
        [RepositoryPackageMarker("pyproject.toml", "pyproject.toml", "python", 1)],
    )
    assert package_map.marker_count == 1


def test_repository_package_map_004_ecosystem_count_manual():
    package_map = RepositoryPackageMap(
        "/repo",
        [
            RepositoryPackageMarker("pyproject.toml", "pyproject.toml", "python", 1),
            RepositoryPackageMarker("package.json", "package.json", "node", 1),
        ],
    )
    assert package_map.ecosystem_count == 2


def test_repository_package_map_005_ecosystems_sorted():
    package_map = RepositoryPackageMap(
        "/repo",
        [
            RepositoryPackageMarker("pyproject.toml", "pyproject.toml", "python", 1),
            RepositoryPackageMarker("package.json", "package.json", "node", 1),
        ],
    )
    assert package_map.ecosystems == ["node", "python"]


def test_repository_package_map_006_root_markers():
    root = RepositoryPackageMarker("package.json", "package.json", "node", 1)
    nested = RepositoryPackageMarker("src/requirements.txt", "requirements.txt", "python", 2)
    package_map = RepositoryPackageMap("/repo", [root, nested])
    assert package_map.root_markers == [root]


def test_repository_package_map_007_has_package_markers_true():
    package_map = RepositoryPackageMap(
        "/repo",
        [RepositoryPackageMarker("package.json", "package.json", "node", 1)],
    )
    assert package_map.has_package_markers is True


def test_repository_package_map_008_has_package_markers_false():
    assert RepositoryPackageMap("/repo").has_package_markers is False


def test_repository_package_map_009_markers_for_ecosystem():
    package_map = RepositoryPackageMap(
        "/repo",
        [
            RepositoryPackageMarker("pyproject.toml", "pyproject.toml", "python", 1),
            RepositoryPackageMarker("package.json", "package.json", "node", 1),
        ],
    )
    assert [m.marker_name for m in package_map.markers_for_ecosystem("python")] == ["pyproject.toml"]


def test_repository_package_map_010_builder_finds_root_python(tmp_path):
    repo = make_repo(tmp_path)
    package_map = RepositoryPackageMapBuilder().build(repo)
    assert "pyproject.toml" in [marker.path for marker in package_map.markers]


def test_repository_package_map_011_builder_finds_root_node(tmp_path):
    repo = make_repo(tmp_path)
    package_map = RepositoryPackageMapBuilder().build(repo)
    assert "package.json" in [marker.path for marker in package_map.markers]


def test_repository_package_map_012_builder_finds_nested_requirements(tmp_path):
    repo = make_repo(tmp_path)
    package_map = RepositoryPackageMapBuilder().build(repo)
    assert "src/requirements.txt" in [marker.path for marker in package_map.markers]


def test_repository_package_map_013_builder_ignores_git(tmp_path):
    repo = make_repo(tmp_path)
    package_map = RepositoryPackageMapBuilder().build(repo)
    assert ".git/package.json" not in [marker.path for marker in package_map.markers]


def test_repository_package_map_014_builder_ecosystem_count(tmp_path):
    repo = make_repo(tmp_path)
    package_map = RepositoryPackageMapBuilder().build(repo)
    assert package_map.ecosystem_count == 2


def test_repository_package_map_015_builder_respects_depth(tmp_path):
    repo = make_repo(tmp_path)
    package_map = RepositoryPackageMapBuilder().build(repo, max_depth=1)
    assert "src/requirements.txt" not in [marker.path for marker in package_map.markers]


def test_repository_package_map_016_builder_missing_path_raises(tmp_path):
    try:
        RepositoryPackageMapBuilder().build(tmp_path / "missing")
        assert False
    except FileNotFoundError:
        assert True


def test_repository_package_map_017_builder_file_path_raises(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")
    try:
        RepositoryPackageMapBuilder().build(file_path)
        assert False
    except NotADirectoryError:
        assert True


def test_repository_package_map_018_summary_no_markers():
    summary = RepositoryPackageMapSummaryBuilder().build(RepositoryPackageMap("/repo"))
    assert summary.outcome == "no_package_markers"


def test_repository_package_map_019_summary_single_ecosystem():
    package_map = RepositoryPackageMap(
        "/repo",
        [RepositoryPackageMarker("pyproject.toml", "pyproject.toml", "python", 1)],
    )
    summary = RepositoryPackageMapSummaryBuilder().build(package_map)
    assert summary.outcome == "single_ecosystem"


def test_repository_package_map_020_summary_multi_ecosystem():
    package_map = RepositoryPackageMap(
        "/repo",
        [
            RepositoryPackageMarker("pyproject.toml", "pyproject.toml", "python", 1),
            RepositoryPackageMarker("package.json", "package.json", "node", 1),
        ],
    )
    summary = RepositoryPackageMapSummaryBuilder().build(package_map)
    assert summary.outcome == "multi_ecosystem"


def test_repository_package_map_021_serialize_counts():
    package_map = RepositoryPackageMap(
        "/repo",
        [RepositoryPackageMarker("package.json", "package.json", "node", 1)],
    )
    response = serialize_repository_package_map(package_map)
    assert response.marker_count == 1
    assert response.ecosystem_count == 1


def test_repository_package_map_022_serialize_summary():
    package_map = RepositoryPackageMap(
        "/repo",
        [RepositoryPackageMarker("package.json", "package.json", "node", 1)],
    )
    response = serialize_repository_package_map(package_map)
    assert response.summary.outcome == "single_ecosystem"


def test_repository_package_map_023_api_returns_200(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-package-map", json={"repository_path": str(repo)})
    assert response.status_code == 200


def test_repository_package_map_024_api_returns_marker_count(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-package-map", json={"repository_path": str(repo)})
    assert response.json()["marker_count"] == 3


def test_repository_package_map_025_api_returns_ecosystems(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-package-map", json={"repository_path": str(repo)})
    assert response.json()["ecosystems"] == ["node", "python"]


def test_repository_package_map_026_api_returns_root_markers(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-package-map", json={"repository_path": str(repo)})
    assert len(response.json()["root_markers"]) == 2


def test_repository_package_map_027_api_respects_depth(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post(
        "/api/v1/repository-package-map",
        json={"repository_path": str(repo), "max_depth": 1},
    )
    paths = [marker["path"] for marker in response.json()["markers"]]
    assert "src/requirements.txt" not in paths


def test_repository_package_map_028_api_rejects_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-package-map",
        json={"repository_path": str(tmp_path / "missing")},
    )
    assert response.status_code == 400


def test_repository_package_map_029_api_rejects_empty_path():
    response = client.post("/api/v1/repository-package-map", json={"repository_path": ""})
    assert response.status_code == 422


def test_repository_package_map_030_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-package-map" in paths
