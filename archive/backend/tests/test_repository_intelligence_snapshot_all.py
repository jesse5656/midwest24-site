import hashlib
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_intelligence_snapshot import (
    serialize_repository_intelligence_snapshot,
)
from app.connectors.repository.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshot,
    RepositoryIntelligenceSnapshotBuilder,
    RepositoryIntelligenceSnapshotMetric,
)
from app.connectors.repository.repository_intelligence_snapshot_summary import (
    RepositoryIntelligenceSnapshotSummaryBuilder,
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


def make_snapshot(
    metrics=None,
    warning_count=0,
    critical_count=0,
    fingerprint="abc123",
):
    return RepositoryIntelligenceSnapshot(
        repository_path="/repo",
        repository_name="repo",
        metrics=metrics or [],
        node_count=10,
        edge_count=8,
        report_section_count=5,
        warning_count=warning_count,
        critical_count=critical_count,
        fingerprint=fingerprint,
    )


def test_snapshot_001_metric_count():
    snapshot = make_snapshot(
        [
            RepositoryIntelligenceSnapshotMetric(
                "files",
                2,
                "healthy",
            )
        ]
    )
    assert snapshot.metric_count == 1


def test_snapshot_002_metric_names():
    snapshot = make_snapshot(
        [
            RepositoryIntelligenceSnapshotMetric(
                "files",
                2,
                "healthy",
            ),
            RepositoryIntelligenceSnapshotMetric(
                "symbols",
                4,
                "healthy",
            ),
        ]
    )
    assert snapshot.metric_names == ["files", "symbols"]


def test_snapshot_003_metric_value():
    snapshot = make_snapshot(
        [
            RepositoryIntelligenceSnapshotMetric(
                "files",
                2,
                "healthy",
            )
        ]
    )
    assert snapshot.metric_value("files") == 2


def test_snapshot_004_metric_value_missing():
    assert make_snapshot().metric_value("missing") is None


def test_snapshot_005_is_healthy():
    assert make_snapshot().is_healthy is True


def test_snapshot_006_warning_not_healthy():
    assert make_snapshot(warning_count=1).is_healthy is False


def test_snapshot_007_critical_not_healthy():
    assert make_snapshot(critical_count=1).is_healthy is False


def test_snapshot_008_canonical_payload_excludes_path():
    snapshot = make_snapshot()
    assert "repository_path" not in snapshot.canonical_payload()


def test_snapshot_009_canonical_payload_excludes_fingerprint():
    snapshot = make_snapshot()
    assert "fingerprint" not in snapshot.canonical_payload()


def test_snapshot_010_canonical_json_deterministic():
    first = make_snapshot(
        [
            RepositoryIntelligenceSnapshotMetric(
                "symbols",
                4,
                "healthy",
            ),
            RepositoryIntelligenceSnapshotMetric(
                "files",
                2,
                "healthy",
            ),
        ]
    )

    second = make_snapshot(
        [
            RepositoryIntelligenceSnapshotMetric(
                "files",
                2,
                "healthy",
            ),
            RepositoryIntelligenceSnapshotMetric(
                "symbols",
                4,
                "healthy",
            ),
        ]
    )

    assert first.canonical_json() == second.canonical_json()


def test_snapshot_011_builder_name(tmp_path):
    snapshot = RepositoryIntelligenceSnapshotBuilder().build(
        make_repo(tmp_path)
    )
    assert snapshot.repository_name == "repo"


def test_snapshot_012_builder_metrics(tmp_path):
    snapshot = RepositoryIntelligenceSnapshotBuilder().build(
        make_repo(tmp_path)
    )
    assert snapshot.metric_count > 0


def test_snapshot_013_builder_nodes(tmp_path):
    snapshot = RepositoryIntelligenceSnapshotBuilder().build(
        make_repo(tmp_path)
    )
    assert snapshot.node_count > 0


def test_snapshot_014_builder_edges(tmp_path):
    snapshot = RepositoryIntelligenceSnapshotBuilder().build(
        make_repo(tmp_path)
    )
    assert snapshot.edge_count > 0


def test_snapshot_015_builder_report_sections(tmp_path):
    snapshot = RepositoryIntelligenceSnapshotBuilder().build(
        make_repo(tmp_path)
    )
    assert snapshot.report_section_count == 5


def test_snapshot_016_builder_fingerprint_length(tmp_path):
    snapshot = RepositoryIntelligenceSnapshotBuilder().build(
        make_repo(tmp_path)
    )
    assert len(snapshot.fingerprint) == 64


def test_snapshot_017_builder_fingerprint_hex(tmp_path):
    snapshot = RepositoryIntelligenceSnapshotBuilder().build(
        make_repo(tmp_path)
    )
    int(snapshot.fingerprint, 16)


def test_snapshot_018_builder_fingerprint_correct(tmp_path):
    snapshot = RepositoryIntelligenceSnapshotBuilder().build(
        make_repo(tmp_path)
    )

    expected = hashlib.sha256(
        snapshot.canonical_json().encode("utf-8")
    ).hexdigest()

    assert snapshot.fingerprint == expected


def test_snapshot_019_builder_deterministic(tmp_path):
    repo = make_repo(tmp_path)

    first = RepositoryIntelligenceSnapshotBuilder().build(repo)
    second = RepositoryIntelligenceSnapshotBuilder().build(repo)

    assert first.fingerprint == second.fingerprint


def test_snapshot_020_missing_path(tmp_path):
    try:
        RepositoryIntelligenceSnapshotBuilder().build(
            tmp_path / "missing"
        )
        assert False
    except FileNotFoundError:
        assert True


def test_snapshot_021_file_path(tmp_path):
    path = tmp_path / "file.py"
    path.write_text("x", encoding="utf-8")

    try:
        RepositoryIntelligenceSnapshotBuilder().build(path)
        assert False
    except NotADirectoryError:
        assert True


def test_snapshot_022_summary_empty():
    summary = RepositoryIntelligenceSnapshotSummaryBuilder().build(
        make_snapshot()
    )
    assert summary.outcome == "empty_snapshot"


def test_snapshot_023_summary_healthy():
    summary = RepositoryIntelligenceSnapshotSummaryBuilder().build(
        make_snapshot(
            [
                RepositoryIntelligenceSnapshotMetric(
                    "files",
                    2,
                    "healthy",
                )
            ]
        )
    )
    assert summary.outcome == "healthy"


def test_snapshot_024_summary_warning():
    summary = RepositoryIntelligenceSnapshotSummaryBuilder().build(
        make_snapshot(
            [
                RepositoryIntelligenceSnapshotMetric(
                    "files",
                    2,
                    "warning",
                )
            ],
            warning_count=1,
        )
    )
    assert summary.outcome == "warnings_detected"


def test_snapshot_025_summary_critical():
    summary = RepositoryIntelligenceSnapshotSummaryBuilder().build(
        make_snapshot(
            [
                RepositoryIntelligenceSnapshotMetric(
                    "files",
                    2,
                    "critical",
                )
            ],
            critical_count=1,
        )
    )
    assert summary.outcome == "critical"


def test_snapshot_026_serialize():
    response = serialize_repository_intelligence_snapshot(
        make_snapshot(
            [
                RepositoryIntelligenceSnapshotMetric(
                    "files",
                    2,
                    "healthy",
                )
            ]
        )
    )
    assert response.metric_count == 1
    assert response.node_count == 10


def test_snapshot_027_api_200(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-snapshot",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.status_code == 200


def test_snapshot_028_api_fingerprint(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-snapshot",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert len(response.json()["fingerprint"]) == 64


def test_snapshot_029_api_metrics(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-snapshot",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.json()["metric_count"] > 0


def test_snapshot_030_api_canonical_json(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-snapshot",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.json()["canonical_json"].startswith("{")


def test_snapshot_031_api_summary(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-snapshot",
        json={
            "repository_path": str(make_repo(tmp_path))
        },
    )
    assert response.json()["summary"]["outcome"] in {
        "healthy",
        "warnings_detected",
        "critical",
    }


def test_snapshot_032_api_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-intelligence-snapshot",
        json={
            "repository_path": str(tmp_path / "missing")
        },
    )
    assert response.status_code == 400


def test_snapshot_033_api_empty_path():
    response = client.post(
        "/api/v1/repository-intelligence-snapshot",
        json={"repository_path": ""},
    )
    assert response.status_code == 422


def test_snapshot_034_route_registered():
    paths = {route.path for route in app.routes}
    assert (
        "/api/v1/repository-intelligence-snapshot"
        in paths
    )


def test_snapshot_035_route_supports_post():
    route = next(
        route
        for route in app.routes
        if (
            route.path
            == "/api/v1/repository-intelligence-snapshot"
        )
    )
    assert "POST" in route.methods
