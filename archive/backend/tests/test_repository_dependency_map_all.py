from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_dependency_map import serialize_repository_dependency_map
from app.connectors.repository.repository_dependency_map import (
    RepositoryDependency,
    RepositoryDependencyMap,
    RepositoryDependencyMapBuilder,
    re_split_requirement_name,
)
from app.connectors.repository.repository_dependency_map_summary import RepositoryDependencyMapSummaryBuilder
from app.main import app

client = TestClient(app)


def make_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "requirements.txt").write_text(
        "fastapi==1.0\npytest>=8\n# comment\n-r base.txt\n",
        encoding="utf-8",
    )

    (repo / "package.json").write_text(
        '{"dependencies":{"react":"latest"},"devDependencies":{"vite":"latest"}}',
        encoding="utf-8",
    )

    (repo / "pyproject.toml").write_text(
        '[project]\ndependencies = ["sqlalchemy>=2", "pydantic"]\n',
        encoding="utf-8",
    )

    (repo / ".git").mkdir()
    (repo / ".git" / "requirements.txt").write_text("ignored\n", encoding="utf-8")

    return repo


def test_dependency_map_001_requirement_name_exact():
    assert re_split_requirement_name("fastapi==1.0") == "fastapi"


def test_dependency_map_002_requirement_name_greater_equal():
    assert re_split_requirement_name("pytest>=8") == "pytest"


def test_dependency_map_003_requirement_name_extra():
    assert re_split_requirement_name("uvicorn[standard]") == "uvicorn"


def test_dependency_map_004_manual_dependency_count():
    dependency_map = RepositoryDependencyMap(
        "/repo",
        [RepositoryDependency("fastapi", "requirements.txt", "python")],
    )
    assert dependency_map.dependency_count == 1


def test_dependency_map_005_manual_ecosystems():
    dependency_map = RepositoryDependencyMap(
        "/repo",
        [
            RepositoryDependency("fastapi", "requirements.txt", "python"),
            RepositoryDependency("react", "package.json", "node"),
        ],
    )
    assert dependency_map.ecosystems == ["node", "python"]


def test_dependency_map_006_manual_ecosystem_count():
    dependency_map = RepositoryDependencyMap(
        "/repo",
        [
            RepositoryDependency("fastapi", "requirements.txt", "python"),
            RepositoryDependency("react", "package.json", "node"),
        ],
    )
    assert dependency_map.ecosystem_count == 2


def test_dependency_map_007_runtime_count():
    dependency_map = RepositoryDependencyMap(
        "/repo",
        [
            RepositoryDependency("fastapi", "requirements.txt", "python", "runtime"),
            RepositoryDependency("vite", "package.json", "node", "development"),
        ],
    )
    assert dependency_map.runtime_count == 1


def test_dependency_map_008_development_count():
    dependency_map = RepositoryDependencyMap(
        "/repo",
        [
            RepositoryDependency("fastapi", "requirements.txt", "python", "runtime"),
            RepositoryDependency("vite", "package.json", "node", "development"),
        ],
    )
    assert dependency_map.development_count == 1


def test_dependency_map_009_dependencies_for_ecosystem():
    dependency_map = RepositoryDependencyMap(
        "/repo",
        [
            RepositoryDependency("fastapi", "requirements.txt", "python"),
            RepositoryDependency("react", "package.json", "node"),
        ],
    )
    assert [d.name for d in dependency_map.dependencies_for_ecosystem("python")] == ["fastapi"]


def test_dependency_map_010_builder_finds_requirements(tmp_path):
    repo = make_repo(tmp_path)
    dependency_map = RepositoryDependencyMapBuilder().build(repo)
    assert "fastapi" in [dependency.name for dependency in dependency_map.dependencies]


def test_dependency_map_011_builder_finds_pytest(tmp_path):
    repo = make_repo(tmp_path)
    dependency_map = RepositoryDependencyMapBuilder().build(repo)
    assert "pytest" in [dependency.name for dependency in dependency_map.dependencies]


def test_dependency_map_012_builder_ignores_requirement_flags(tmp_path):
    repo = make_repo(tmp_path)
    dependency_map = RepositoryDependencyMapBuilder().build(repo)
    assert "-r" not in [dependency.name for dependency in dependency_map.dependencies]


def test_dependency_map_013_builder_finds_package_json_runtime(tmp_path):
    repo = make_repo(tmp_path)
    dependency_map = RepositoryDependencyMapBuilder().build(repo)
    assert "react" in [dependency.name for dependency in dependency_map.dependencies]


def test_dependency_map_014_builder_finds_package_json_dev(tmp_path):
    repo = make_repo(tmp_path)
    dependency_map = RepositoryDependencyMapBuilder().build(repo)
    dev = [dependency for dependency in dependency_map.dependencies if dependency.name == "vite"][0]
    assert dev.dependency_type == "development"


def test_dependency_map_015_builder_finds_pyproject_dependencies(tmp_path):
    repo = make_repo(tmp_path)
    dependency_map = RepositoryDependencyMapBuilder().build(repo)
    assert "sqlalchemy" in [dependency.name for dependency in dependency_map.dependencies]


def test_dependency_map_016_builder_finds_pyproject_plain_dependency(tmp_path):
    repo = make_repo(tmp_path)
    dependency_map = RepositoryDependencyMapBuilder().build(repo)
    assert "pydantic" in [dependency.name for dependency in dependency_map.dependencies]


def test_dependency_map_017_builder_ignores_git(tmp_path):
    repo = make_repo(tmp_path)
    dependency_map = RepositoryDependencyMapBuilder().build(repo)
    assert "ignored" not in [dependency.name for dependency in dependency_map.dependencies]


def test_dependency_map_018_builder_dependency_count(tmp_path):
    repo = make_repo(tmp_path)
    dependency_map = RepositoryDependencyMapBuilder().build(repo)
    assert dependency_map.dependency_count == 6


def test_dependency_map_019_builder_ecosystems(tmp_path):
    repo = make_repo(tmp_path)
    dependency_map = RepositoryDependencyMapBuilder().build(repo)
    assert dependency_map.ecosystems == ["node", "python"]


def test_dependency_map_020_builder_respects_depth(tmp_path):
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "requirements.txt").write_text("fastapi\n", encoding="utf-8")
    dependency_map = RepositoryDependencyMapBuilder().build(repo, max_depth=1)
    assert dependency_map.dependency_count == 0


def test_dependency_map_021_builder_missing_path_raises(tmp_path):
    try:
        RepositoryDependencyMapBuilder().build(tmp_path / "missing")
        assert False
    except FileNotFoundError:
        assert True


def test_dependency_map_022_builder_file_path_raises(tmp_path):
    path = tmp_path / "file.txt"
    path.write_text("x", encoding="utf-8")
    try:
        RepositoryDependencyMapBuilder().build(path)
        assert False
    except NotADirectoryError:
        assert True


def test_dependency_map_023_invalid_package_json_ignored(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text("{bad", encoding="utf-8")
    dependency_map = RepositoryDependencyMapBuilder().build(repo)
    assert dependency_map.dependency_count == 0


def test_dependency_map_024_summary_no_dependencies():
    summary = RepositoryDependencyMapSummaryBuilder().build(RepositoryDependencyMap("/repo"))
    assert summary.outcome == "no_dependencies"


def test_dependency_map_025_summary_single_ecosystem():
    dependency_map = RepositoryDependencyMap(
        "/repo",
        [RepositoryDependency("fastapi", "requirements.txt", "python")],
    )
    summary = RepositoryDependencyMapSummaryBuilder().build(dependency_map)
    assert summary.outcome == "single_ecosystem_dependencies"


def test_dependency_map_026_summary_multi_ecosystem():
    dependency_map = RepositoryDependencyMap(
        "/repo",
        [
            RepositoryDependency("fastapi", "requirements.txt", "python"),
            RepositoryDependency("react", "package.json", "node"),
        ],
    )
    summary = RepositoryDependencyMapSummaryBuilder().build(dependency_map)
    assert summary.outcome == "multi_ecosystem_dependencies"


def test_dependency_map_027_serialize_counts():
    dependency_map = RepositoryDependencyMap(
        "/repo",
        [RepositoryDependency("fastapi", "requirements.txt", "python")],
    )
    response = serialize_repository_dependency_map(dependency_map)
    assert response.dependency_count == 1


def test_dependency_map_028_serialize_summary():
    dependency_map = RepositoryDependencyMap(
        "/repo",
        [RepositoryDependency("fastapi", "requirements.txt", "python")],
    )
    response = serialize_repository_dependency_map(dependency_map)
    assert response.summary.outcome == "single_ecosystem_dependencies"


def test_dependency_map_029_api_returns_200(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-dependency-map", json={"repository_path": str(repo)})
    assert response.status_code == 200


def test_dependency_map_030_api_returns_dependency_count(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-dependency-map", json={"repository_path": str(repo)})
    assert response.json()["dependency_count"] == 6


def test_dependency_map_031_api_returns_ecosystems(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-dependency-map", json={"repository_path": str(repo)})
    assert response.json()["ecosystems"] == ["node", "python"]


def test_dependency_map_032_api_returns_runtime_count(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-dependency-map", json={"repository_path": str(repo)})
    assert response.json()["runtime_count"] == 5


def test_dependency_map_033_api_returns_development_count(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-dependency-map", json={"repository_path": str(repo)})
    assert response.json()["development_count"] == 1


def test_dependency_map_034_api_rejects_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-dependency-map",
        json={"repository_path": str(tmp_path / "missing")},
    )
    assert response.status_code == 400


def test_dependency_map_035_api_rejects_empty_path():
    response = client.post("/api/v1/repository-dependency-map", json={"repository_path": ""})
    assert response.status_code == 422


def test_dependency_map_036_api_respects_depth(tmp_path):
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "requirements.txt").write_text("fastapi\n", encoding="utf-8")
    response = client.post(
        "/api/v1/repository-dependency-map",
        json={"repository_path": str(repo), "max_depth": 1},
    )
    assert response.json()["dependency_count"] == 0


def test_dependency_map_037_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-dependency-map" in paths


def test_dependency_map_038_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/repository-dependency-map")
    assert "POST" in route.methods
