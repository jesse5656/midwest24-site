from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_intelligence_dashboard import (
    serialize_repository_intelligence_dashboard,
)
from app.connectors.repository.repository_intelligence_dashboard import (
    RepositoryIntelligenceDashboard,
    RepositoryIntelligenceDashboardBuilder,
    RepositoryIntelligenceMetric,
)
from app.connectors.repository.repository_intelligence_dashboard_summary import (
    RepositoryIntelligenceDashboardSummaryBuilder,
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


def make_dashboard(
    metrics=None,
    warnings=None,
):
    return RepositoryIntelligenceDashboard(
        repository_path="/repo",
        repository_name="repo",
        metrics=metrics or [],
        warnings=warnings or [],
    )


def test_dashboard_001_metric_count():
    dashboard = make_dashboard(
        [
            RepositoryIntelligenceMetric(
                "files",
                1,
                "healthy",
            )
        ]
    )
    assert dashboard.metric_count == 1


def test_dashboard_002_warning_count():
    dashboard = make_dashboard(warnings=["warning"])
    assert dashboard.warning_count == 1


def test_dashboard_003_healthy_metric_count():
    dashboard = make_dashboard(
        [
            RepositoryIntelligenceMetric(
                "files",
                1,
                "healthy",
            ),
            RepositoryIntelligenceMetric(
                "imports",
                0,
                "warning",
            ),
        ]
    )
    assert dashboard.healthy_metric_count == 1


def test_dashboard_004_warning_metric_count():
    dashboard = make_dashboard(
        [
            RepositoryIntelligenceMetric(
                "imports",
                0,
                "warning",
            )
        ]
    )
    assert dashboard.warning_metric_count == 1


def test_dashboard_005_critical_metric_count():
    dashboard = make_dashboard(
        [
            RepositoryIntelligenceMetric(
                "architecture",
                1,
                "critical",
            )
        ]
    )
    assert dashboard.critical_metric_count == 1


def test_dashboard_006_is_healthy():
    dashboard = make_dashboard(
        [
            RepositoryIntelligenceMetric(
                "files",
                1,
                "healthy",
            )
        ]
    )
    assert dashboard.is_healthy is True


def test_dashboard_007_is_not_healthy():
    dashboard = make_dashboard(
        [
            RepositoryIntelligenceMetric(
                "files",
                0,
                "warning",
            )
        ],
        ["metric_warning:files"],
    )
    assert dashboard.is_healthy is False


def test_dashboard_008_metric_names():
    dashboard = make_dashboard(
        [
            RepositoryIntelligenceMetric(
                "files",
                1,
                "healthy",
            ),
            RepositoryIntelligenceMetric(
                "symbols",
                2,
                "healthy",
            ),
        ]
    )
    assert dashboard.metric_names == [
        "files",
        "symbols",
    ]


def test_dashboard_009_metric_value():
    dashboard = make_dashboard(
        [
            RepositoryIntelligenceMetric(
                "files",
                4,
                "healthy",
            )
        ]
    )
    assert dashboard.metric_value("files") == 4


def test_dashboard_010_metric_value_missing():
    assert make_dashboard().metric_value("missing") is None


def test_dashboard_011_metrics_by_status():
    dashboard = make_dashboard(
        [
            RepositoryIntelligenceMetric(
                "files",
                1,
                "healthy",
            ),
            RepositoryIntelligenceMetric(
                "imports",
                0,
                "warning",
            ),
        ]
    )
    assert [
        metric.name
        for metric in dashboard.metrics_by_status("warning")
    ] == ["imports"]


def test_dashboard_012_builder_name(tmp_path):
    dashboard = RepositoryIntelligenceDashboardBuilder().build(
        make_repo(tmp_path)
    )
    assert dashboard.repository_name == "repo"


def test_dashboard_013_builder_metric_count(tmp_path):
    dashboard = RepositoryIntelligenceDashboardBuilder().build(
        make_repo(tmp_path)
    )
    assert dashboard.metric_count == 10


def test_dashboard_014_builder_graph_nodes(tmp_path):
    dashboard = RepositoryIntelligenceDashboardBuilder().build(
        make_repo(tmp_path)
    )
    assert dashboard.metric_value(
        "knowledge_graph_nodes"
    ) > 0


def test_dashboard_015_builder_graph_edges(tmp_path):
    dashboard = RepositoryIntelligenceDashboardBuilder().build(
        make_repo(tmp_path)
    )
    assert dashboard.metric_value(
        "knowledge_graph_edges"
    ) > 0


def test_dashboard_016_builder_files(tmp_path):
    dashboard = RepositoryIntelligenceDashboardBuilder().build(
        make_repo(tmp_path)
    )
    assert dashboard.metric_value("file_nodes") >= 2


def test_dashboard_017_builder_dependencies(tmp_path):
    dashboard = RepositoryIntelligenceDashboardBuilder().build(
        make_repo(tmp_path)
    )
    assert dashboard.metric_value(
        "dependency_nodes"
    ) == 2


def test_dashboard_018_builder_imports(tmp_path):
    dashboard = RepositoryIntelligenceDashboardBuilder().build(
        make_repo(tmp_path)
    )
    assert dashboard.metric_value("import_nodes") == 1


def test_dashboard_019_builder_symbols(tmp_path):
    dashboard = RepositoryIntelligenceDashboardBuilder().build(
        make_repo(tmp_path)
    )
    assert dashboard.metric_value("symbol_nodes") >= 3


def test_dashboard_020_builder_search_documents(tmp_path):
    dashboard = RepositoryIntelligenceDashboardBuilder().build(
        make_repo(tmp_path)
    )
    assert dashboard.metric_value(
        "search_documents"
    ) > 0


def test_dashboard_021_builder_summary_sections(tmp_path):
    dashboard = RepositoryIntelligenceDashboardBuilder().build(
        make_repo(tmp_path)
    )
    assert dashboard.metric_value(
        "summary_sections"
    ) > 0


def test_dashboard_022_builder_healthy(tmp_path):
    dashboard = RepositoryIntelligenceDashboardBuilder().build(
        make_repo(tmp_path)
    )
    assert dashboard.is_healthy is True


def test_dashboard_023_missing_path(tmp_path):
    try:
        RepositoryIntelligenceDashboardBuilder().build(
            tmp_path / "missing"
        )
        assert False
    except FileNotFoundError:
        assert True


def test_dashboard_024_file_path(tmp_path):
    path = tmp_path / "file.py"
    path.write_text("x", encoding="utf-8")

    try:
        RepositoryIntelligenceDashboardBuilder().build(path)
        assert False
    except NotADirectoryError:
        assert True


def test_dashboard_025_summary_empty():
    summary = RepositoryIntelligenceDashboardSummaryBuilder().build(
        make_dashboard()
    )
    assert summary.outcome == "empty_dashboard"


def test_dashboard_026_summary_healthy():
    summary = RepositoryIntelligenceDashboardSummaryBuilder().build(
        make_dashboard(
            [
                RepositoryIntelligenceMetric(
                    "files",
                    1,
                    "healthy",
                )
            ]
        )
    )
    assert summary.outcome == "healthy"


def test_dashboard_027_summary_warning():
    summary = RepositoryIntelligenceDashboardSummaryBuilder().build(
        make_dashboard(
            [
                RepositoryIntelligenceMetric(
                    "files",
                    0,
                    "warning",
                )
            ],
            ["metric_warning:files"],
        )
    )
    assert summary.outcome == "warnings_detected"


def test_dashboard_028_summary_critical():
    summary = RepositoryIntelligenceDashboardSummaryBuilder().build(
        make_dashboard(
            [
                RepositoryIntelligenceMetric(
                    "architecture",
                    1,
                    "critical",
                )
            ]
        )
    )
    assert summary.outcome == "critical"


def test_dashboard_029_serialize():
    response = serialize_repository_intelligence_dashboard(
        make_dashboard(
            [
                RepositoryIntelligenceMetric(
                    "files",
                    1,
                    "healthy",
                    "Files.",
                )
            ]
        )
    )
    assert response.metric_count == 1
    assert response.is_healthy is True


def test_dashboard_030_api_200(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-dashboard",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.status_code == 200


def test_dashboard_031_api_metrics(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-dashboard",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.json()["metric_count"] == 10


def test_dashboard_032_api_healthy(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-dashboard",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.json()["is_healthy"] is True


def test_dashboard_033_api_summary(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-dashboard",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.json()["summary"]["outcome"] == "healthy"


def test_dashboard_034_api_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-dashboard",
        json={
            "repository_path": str(tmp_path / "missing")
        },
    )
    assert response.status_code == 400


def test_dashboard_035_api_empty_path():
    response = client.post(
        "/api/v1/repository-intelligence-dashboard",
        json={"repository_path": ""},
    )
    assert response.status_code == 422


def test_dashboard_036_route_registered():
    paths = {route.path for route in app.routes}
    assert (
        "/api/v1/repository-intelligence-dashboard"
        in paths
    )


def test_dashboard_037_route_supports_post():
    route = next(
        route
        for route in app.routes
        if (
            route.path
            == "/api/v1/repository-intelligence-dashboard"
        )
    )
    assert "POST" in route.methods
