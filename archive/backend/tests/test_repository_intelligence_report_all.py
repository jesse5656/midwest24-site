from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_intelligence_report import (
    serialize_repository_intelligence_report,
)
from app.connectors.repository.repository_intelligence_report import (
    RepositoryIntelligenceReport,
    RepositoryIntelligenceReportBuilder,
    RepositoryIntelligenceReportSection,
)
from app.connectors.repository.repository_intelligence_report_summary import (
    RepositoryIntelligenceReportSummaryBuilder,
)
from app.main import app

client = TestClient(app)


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "requirements.txt").write_text(
        "fastapi\npytest\n",
        encoding="utf-8",
    )

    (repo / "app.py").write_text(
        "import os\n"
        "MAX_SIZE = 10\n"
        "class Worker:\n"
        "    def run(self):\n"
        "        return os.getcwd()\n",
        encoding="utf-8",
    )

    return repo


def make_report(
    sections=None,
):
    return RepositoryIntelligenceReport(
        repository_path="/repo",
        repository_name="repo",
        title="Repository Intelligence Report",
        sections=sections or [],
    )


def test_report_001_section_count():
    report = make_report(
        [
            RepositoryIntelligenceReportSection(
                "Summary",
                "Content",
            )
        ]
    )
    assert report.section_count == 1


def test_report_002_section_names():
    report = make_report(
        [
            RepositoryIntelligenceReportSection(
                "Summary",
                "Content",
            )
        ]
    )
    assert report.section_names == ["Summary"]


def test_report_003_info_count():
    report = make_report(
        [
            RepositoryIntelligenceReportSection(
                "Summary",
                "Content",
                "info",
            )
        ]
    )
    assert report.info_count == 1


def test_report_004_warning_count():
    report = make_report(
        [
            RepositoryIntelligenceReportSection(
                "Warnings",
                "Content",
                "warning",
            )
        ]
    )
    assert report.warning_count == 1


def test_report_005_critical_count():
    report = make_report(
        [
            RepositoryIntelligenceReportSection(
                "Critical",
                "Content",
                "critical",
            )
        ]
    )
    assert report.critical_count == 1


def test_report_006_is_healthy():
    report = make_report(
        [
            RepositoryIntelligenceReportSection(
                "Summary",
                "Content",
                "info",
            )
        ]
    )
    assert report.is_healthy is True


def test_report_007_is_not_healthy():
    report = make_report(
        [
            RepositoryIntelligenceReportSection(
                "Warnings",
                "Content",
                "warning",
            )
        ]
    )
    assert report.is_healthy is False


def test_report_008_section_content():
    report = make_report(
        [
            RepositoryIntelligenceReportSection(
                "Summary",
                "Content",
            )
        ]
    )
    assert report.section_content("Summary") == "Content"


def test_report_009_section_content_missing():
    assert make_report().section_content("Missing") is None


def test_report_010_sections_by_status():
    report = make_report(
        [
            RepositoryIntelligenceReportSection(
                "Summary",
                "Content",
                "info",
            ),
            RepositoryIntelligenceReportSection(
                "Warnings",
                "Content",
                "warning",
            ),
        ]
    )
    assert [
        section.name
        for section in report.sections_by_status("warning")
    ] == ["Warnings"]


def test_report_011_markdown_title():
    report = make_report(
        [
            RepositoryIntelligenceReportSection(
                "Summary",
                "Content",
            )
        ]
    )
    assert report.as_markdown().startswith(
        "# Repository Intelligence Report"
    )


def test_report_012_markdown_section():
    report = make_report(
        [
            RepositoryIntelligenceReportSection(
                "Summary",
                "Content",
            )
        ]
    )
    assert "## Summary" in report.as_markdown()


def test_report_013_builder_title(tmp_path):
    report = RepositoryIntelligenceReportBuilder().build(
        make_repo(tmp_path)
    )
    assert report.title == (
        "repo Repository Intelligence Report"
    )


def test_report_014_builder_section_count(tmp_path):
    report = RepositoryIntelligenceReportBuilder().build(
        make_repo(tmp_path)
    )
    assert report.section_count == 5


def test_report_015_builder_executive_summary(tmp_path):
    report = RepositoryIntelligenceReportBuilder().build(
        make_repo(tmp_path)
    )
    assert report.section_content(
        "Executive Summary"
    ) is not None


def test_report_016_builder_metrics(tmp_path):
    report = RepositoryIntelligenceReportBuilder().build(
        make_repo(tmp_path)
    )
    content = report.section_content(
        "Repository Metrics"
    )
    assert "knowledge_graph_nodes" in content


def test_report_017_builder_repository_summary(tmp_path):
    report = RepositoryIntelligenceReportBuilder().build(
        make_repo(tmp_path)
    )
    content = report.section_content(
        "Repository Summary"
    )
    assert "Repository" in content


def test_report_018_builder_architecture(tmp_path):
    report = RepositoryIntelligenceReportBuilder().build(
        make_repo(tmp_path)
    )
    content = report.section_content(
        "Architecture Findings"
    )
    assert "knowledge_graph_available" in content


def test_report_019_builder_warnings(tmp_path):
    report = RepositoryIntelligenceReportBuilder().build(
        make_repo(tmp_path)
    )
    assert report.section_content("Warnings") is not None


def test_report_020_builder_markdown(tmp_path):
    report = RepositoryIntelligenceReportBuilder().build(
        make_repo(tmp_path)
    )
    assert "# repo Repository Intelligence Report" in (
        report.as_markdown()
    )


def test_report_021_missing_path(tmp_path):
    try:
        RepositoryIntelligenceReportBuilder().build(
            tmp_path / "missing"
        )
        assert False
    except FileNotFoundError:
        assert True


def test_report_022_file_path(tmp_path):
    path = tmp_path / "file.py"
    path.write_text("x", encoding="utf-8")

    try:
        RepositoryIntelligenceReportBuilder().build(path)
        assert False
    except NotADirectoryError:
        assert True


def test_report_023_summary_empty():
    summary = RepositoryIntelligenceReportSummaryBuilder().build(
        make_report()
    )
    assert summary.outcome == "empty_report"


def test_report_024_summary_healthy():
    summary = RepositoryIntelligenceReportSummaryBuilder().build(
        make_report(
            [
                RepositoryIntelligenceReportSection(
                    "Summary",
                    "Content",
                    "info",
                )
            ]
        )
    )
    assert summary.outcome == "healthy"


def test_report_025_summary_warning():
    summary = RepositoryIntelligenceReportSummaryBuilder().build(
        make_report(
            [
                RepositoryIntelligenceReportSection(
                    "Warnings",
                    "Content",
                    "warning",
                )
            ]
        )
    )
    assert summary.outcome == "warnings_detected"


def test_report_026_summary_critical():
    summary = RepositoryIntelligenceReportSummaryBuilder().build(
        make_report(
            [
                RepositoryIntelligenceReportSection(
                    "Critical",
                    "Content",
                    "critical",
                )
            ]
        )
    )
    assert summary.outcome == "critical_findings"


def test_report_027_serialize():
    response = serialize_repository_intelligence_report(
        make_report(
            [
                RepositoryIntelligenceReportSection(
                    "Summary",
                    "Content",
                )
            ]
        )
    )
    assert response.section_count == 1
    assert response.markdown.startswith(
        "# Repository Intelligence Report"
    )


def test_report_028_api_200(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-report",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.status_code == 200


def test_report_029_api_sections(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-report",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.json()["section_count"] == 5


def test_report_030_api_markdown(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-report",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.json()["markdown"].startswith(
        "# repo Repository Intelligence Report"
    )


def test_report_031_api_summary(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-report",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.json()["summary"]["outcome"] in {
        "healthy",
        "warnings_detected",
    }


def test_report_032_api_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-report",
        json={
            "repository_path": str(tmp_path / "missing")
        },
    )
    assert response.status_code == 400


def test_report_033_api_empty_path():
    response = client.post(
        "/api/v1/repository-intelligence-report",
        json={"repository_path": ""},
    )
    assert response.status_code == 422


def test_report_034_route_registered():
    paths = {route.path for route in app.routes}
    assert (
        "/api/v1/repository-intelligence-report"
        in paths
    )


def test_report_035_route_supports_post():
    route = next(
        route
        for route in app.routes
        if (
            route.path
            == "/api/v1/repository-intelligence-report"
        )
    )
    assert "POST" in route.methods
