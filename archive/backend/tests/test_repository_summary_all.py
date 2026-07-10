from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_summary import serialize_repository_summary
from app.connectors.repository.repository_summary import (
    RepositorySummary,
    RepositorySummaryBuilder,
    RepositorySummarySection,
)
from app.connectors.repository.repository_summary_summary import RepositorySummarySummaryBuilder
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


def test_repository_summary_001_section_count():
    summary = RepositorySummary("/repo", "Title", [RepositorySummarySection("A", "1")])
    assert summary.section_count == 1


def test_repository_summary_002_section_names():
    summary = RepositorySummary("/repo", "Title", [RepositorySummarySection("A", "1")])
    assert summary.section_names == ["A"]


def test_repository_summary_003_section_value_found():
    summary = RepositorySummary("/repo", "Title", [RepositorySummarySection("A", "1")])
    assert summary.section_value("A") == "1"


def test_repository_summary_004_section_value_missing():
    summary = RepositorySummary("/repo", "Title", [RepositorySummarySection("A", "1")])
    assert summary.section_value("B") is None


def test_repository_summary_005_builder_title(tmp_path):
    repo = make_repo(tmp_path)
    summary = RepositorySummaryBuilder().build(repo)
    assert summary.title == "repo Repository Summary"


def test_repository_summary_006_builder_has_repository_section(tmp_path):
    repo = make_repo(tmp_path)
    summary = RepositorySummaryBuilder().build(repo)
    assert summary.section_value("Repository") == "repo"


def test_repository_summary_007_builder_has_files_section(tmp_path):
    repo = make_repo(tmp_path)
    summary = RepositorySummaryBuilder().build(repo)
    assert int(summary.section_value("Files")) >= 2


def test_repository_summary_008_builder_has_dependencies_section(tmp_path):
    repo = make_repo(tmp_path)
    summary = RepositorySummaryBuilder().build(repo)
    assert int(summary.section_value("Dependencies")) == 1


def test_repository_summary_009_builder_has_imports_section(tmp_path):
    repo = make_repo(tmp_path)
    summary = RepositorySummaryBuilder().build(repo)
    assert int(summary.section_value("Imports")) == 1


def test_repository_summary_010_builder_has_symbols_section(tmp_path):
    repo = make_repo(tmp_path)
    summary = RepositorySummaryBuilder().build(repo)
    assert int(summary.section_value("Symbols")) >= 2


def test_repository_summary_011_builder_missing_path_raises(tmp_path):
    try:
        RepositorySummaryBuilder().build(tmp_path / "missing")
        assert False
    except FileNotFoundError:
        assert True


def test_repository_summary_012_builder_file_path_raises(tmp_path):
    path = tmp_path / "file.py"
    path.write_text("x", encoding="utf-8")
    try:
        RepositorySummaryBuilder().build(path)
        assert False
    except NotADirectoryError:
        assert True


def test_repository_summary_013_status_empty():
    status = RepositorySummarySummaryBuilder().build(RepositorySummary("/repo", "Title", []))
    assert status.outcome == "empty_summary"


def test_repository_summary_014_status_built():
    status = RepositorySummarySummaryBuilder().build(
        RepositorySummary("/repo", "Title", [RepositorySummarySection("A", "1")])
    )
    assert status.outcome == "summary_built"


def test_repository_summary_015_status_no_action():
    status = RepositorySummarySummaryBuilder().build(
        RepositorySummary("/repo", "Title", [RepositorySummarySection("A", "1")])
    )
    assert status.action_required is False


def test_repository_summary_016_serialize_counts():
    response = serialize_repository_summary(
        RepositorySummary("/repo", "Title", [RepositorySummarySection("A", "1")])
    )
    assert response.section_count == 1


def test_repository_summary_017_serialize_summary():
    response = serialize_repository_summary(
        RepositorySummary("/repo", "Title", [RepositorySummarySection("A", "1")])
    )
    assert response.summary.outcome == "summary_built"


def test_repository_summary_018_api_returns_200(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-summary", json={"repository_path": str(repo)})
    assert response.status_code == 200


def test_repository_summary_019_api_returns_title(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-summary", json={"repository_path": str(repo)})
    assert response.json()["title"] == "repo Repository Summary"


def test_repository_summary_020_api_returns_sections(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-summary", json={"repository_path": str(repo)})
    assert response.json()["section_count"] == 8


def test_repository_summary_021_api_returns_summary_status(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-summary", json={"repository_path": str(repo)})
    assert response.json()["summary"]["outcome"] == "summary_built"


def test_repository_summary_022_api_rejects_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-summary",
        json={"repository_path": str(tmp_path / "missing")},
    )
    assert response.status_code == 400


def test_repository_summary_023_api_rejects_empty_path():
    response = client.post("/api/v1/repository-summary", json={"repository_path": ""})
    assert response.status_code == 422


def test_repository_summary_024_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-summary" in paths


def test_repository_summary_025_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/repository-summary")
    assert "POST" in route.methods
