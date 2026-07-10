from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_architecture_report import serialize_repository_architecture_report
from app.connectors.repository.repository_architecture_report import (
    RepositoryArchitectureFinding,
    RepositoryArchitectureReport,
    RepositoryArchitectureReportBuilder,
)
from app.connectors.repository.repository_architecture_report_summary import (
    RepositoryArchitectureReportSummaryBuilder,
)
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


def test_arch_report_001_finding_count():
    report = RepositoryArchitectureReport(
        "/repo",
        "Title",
        [RepositoryArchitectureFinding("a", "info", "message")],
    )
    assert report.finding_count == 1


def test_arch_report_002_severity_levels():
    report = RepositoryArchitectureReport(
        "/repo",
        "Title",
        [
            RepositoryArchitectureFinding("a", "warning", "message"),
            RepositoryArchitectureFinding("b", "info", "message"),
        ],
    )
    assert report.severity_levels == ["info", "warning"]


def test_arch_report_003_info_count():
    report = RepositoryArchitectureReport(
        "/repo",
        "Title",
        [RepositoryArchitectureFinding("a", "info", "message")],
    )
    assert report.info_count == 1


def test_arch_report_004_warning_count():
    report = RepositoryArchitectureReport(
        "/repo",
        "Title",
        [RepositoryArchitectureFinding("a", "warning", "message")],
    )
    assert report.warning_count == 1


def test_arch_report_005_critical_count():
    report = RepositoryArchitectureReport(
        "/repo",
        "Title",
        [RepositoryArchitectureFinding("a", "critical", "message")],
    )
    assert report.critical_count == 1


def test_arch_report_006_has_warnings_true():
    report = RepositoryArchitectureReport(
        "/repo",
        "Title",
        [RepositoryArchitectureFinding("a", "warning", "message")],
    )
    assert report.has_warnings is True


def test_arch_report_007_has_warnings_false():
    report = RepositoryArchitectureReport(
        "/repo",
        "Title",
        [RepositoryArchitectureFinding("a", "info", "message")],
    )
    assert report.has_warnings is False


def test_arch_report_008_findings_by_severity():
    report = RepositoryArchitectureReport(
        "/repo",
        "Title",
        [
            RepositoryArchitectureFinding("a", "warning", "message"),
            RepositoryArchitectureFinding("b", "info", "message"),
        ],
    )
    assert [finding.name for finding in report.findings_by_severity("warning")] == ["a"]


def test_arch_report_009_builder_title(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositoryArchitectureReportBuilder().build(repo)
    assert report.title == "repo Architecture Report"


def test_arch_report_010_builder_has_findings(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositoryArchitectureReportBuilder().build(repo)
    assert report.finding_count == 6


def test_arch_report_011_builder_has_graph_finding(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositoryArchitectureReportBuilder().build(repo)
    names = [finding.name for finding in report.findings]
    assert "knowledge_graph_available" in names


def test_arch_report_012_builder_has_symbol_finding(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositoryArchitectureReportBuilder().build(repo)
    names = [finding.name for finding in report.findings]
    assert "symbol_inventory_available" in names


def test_arch_report_013_builder_has_dependency_finding(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositoryArchitectureReportBuilder().build(repo)
    names = [finding.name for finding in report.findings]
    assert "dependency_inventory_available" in names


def test_arch_report_014_builder_missing_path_raises(tmp_path):
    try:
        RepositoryArchitectureReportBuilder().build(tmp_path / "missing")
        assert False
    except FileNotFoundError:
        assert True


def test_arch_report_015_builder_file_path_raises(tmp_path):
    path = tmp_path / "file.py"
    path.write_text("x", encoding="utf-8")
    try:
        RepositoryArchitectureReportBuilder().build(path)
        assert False
    except NotADirectoryError:
        assert True


def test_arch_report_016_summary_empty():
    summary = RepositoryArchitectureReportSummaryBuilder().build(
        RepositoryArchitectureReport("/repo", "Title", [])
    )
    assert summary.outcome == "empty_report"


def test_arch_report_017_summary_healthy():
    summary = RepositoryArchitectureReportSummaryBuilder().build(
        RepositoryArchitectureReport("/repo", "Title", [RepositoryArchitectureFinding("a", "info", "message")])
    )
    assert summary.outcome == "healthy"


def test_arch_report_018_summary_warning():
    summary = RepositoryArchitectureReportSummaryBuilder().build(
        RepositoryArchitectureReport("/repo", "Title", [RepositoryArchitectureFinding("a", "warning", "message")])
    )
    assert summary.outcome == "warnings_detected"


def test_arch_report_019_summary_warning_action_required():
    summary = RepositoryArchitectureReportSummaryBuilder().build(
        RepositoryArchitectureReport("/repo", "Title", [RepositoryArchitectureFinding("a", "warning", "message")])
    )
    assert summary.action_required is True


def test_arch_report_020_serialize_counts():
    response = serialize_repository_architecture_report(
        RepositoryArchitectureReport("/repo", "Title", [RepositoryArchitectureFinding("a", "info", "message")])
    )
    assert response.finding_count == 1
    assert response.info_count == 1


def test_arch_report_021_serialize_summary():
    response = serialize_repository_architecture_report(
        RepositoryArchitectureReport("/repo", "Title", [RepositoryArchitectureFinding("a", "info", "message")])
    )
    assert response.summary.outcome == "healthy"


def test_arch_report_022_api_returns_200(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-architecture-report", json={"repository_path": str(repo)})
    assert response.status_code == 200


def test_arch_report_023_api_returns_title(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-architecture-report", json={"repository_path": str(repo)})
    assert response.json()["title"] == "repo Architecture Report"


def test_arch_report_024_api_returns_findings(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-architecture-report", json={"repository_path": str(repo)})
    assert response.json()["finding_count"] == 6


def test_arch_report_025_api_returns_summary(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-architecture-report", json={"repository_path": str(repo)})
    assert response.json()["summary"]["outcome"] == "healthy"


def test_arch_report_026_api_rejects_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-architecture-report",
        json={"repository_path": str(tmp_path / "missing")},
    )
    assert response.status_code == 400


def test_arch_report_027_api_rejects_empty_path():
    response = client.post("/api/v1/repository-architecture-report", json={"repository_path": ""})
    assert response.status_code == 422


def test_arch_report_028_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-architecture-report" in paths


def test_arch_report_029_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/repository-architecture-report")
    assert "POST" in route.methods
