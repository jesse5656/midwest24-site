from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_snapshot_comparison import (
    serialize_repository_snapshot_comparison,
)
from app.connectors.repository.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshot,
    RepositoryIntelligenceSnapshotMetric,
)
from app.connectors.repository.repository_snapshot_comparison import (
    RepositorySnapshotComparison,
    RepositorySnapshotComparisonBuilder,
    RepositorySnapshotMetricChange,
)
from app.connectors.repository.repository_snapshot_comparison_summary import (
    RepositorySnapshotComparisonSummaryBuilder,
)
from app.main import app

client = TestClient(app)


def make_repo(
    root: Path,
    changed: bool = False,
) -> Path:
    root.mkdir()

    root.joinpath("requirements.txt").write_text(
        (
            "fastapi\npytest\nsqlalchemy\n"
            if changed
            else "fastapi\npytest\n"
        ),
        encoding="utf-8",
    )

    root.joinpath("app.py").write_text(
        (
            "import os\n"
            "import json\n"
            "class Worker:\n"
            "    def run(self):\n"
            "        return json.dumps({})\n"
            if changed
            else
            "import os\n"
            "class Worker:\n"
            "    def run(self):\n"
            "        return os.getcwd()\n"
        ),
        encoding="utf-8",
    )

    if changed:
        root.joinpath("extra.py").write_text(
            "def extra_function():\n"
            "    return True\n",
            encoding="utf-8",
        )

    return root


def make_snapshot(
    path: str,
    fingerprint: str,
    metrics=None,
    node_count=10,
    edge_count=8,
    warning_count=0,
    critical_count=0,
):
    return RepositoryIntelligenceSnapshot(
        repository_path=path,
        repository_name="repo",
        metrics=metrics or [],
        node_count=node_count,
        edge_count=edge_count,
        report_section_count=5,
        warning_count=warning_count,
        critical_count=critical_count,
        fingerprint=fingerprint,
    )


def test_comparison_001_fingerprints_match():
    comparison = RepositorySnapshotComparison(
        "/a",
        "/b",
        "same",
        "same",
    )
    assert comparison.fingerprints_match is True


def test_comparison_002_fingerprints_differ():
    comparison = RepositorySnapshotComparison(
        "/a",
        "/b",
        "one",
        "two",
    )
    assert comparison.fingerprints_match is False


def test_comparison_003_no_changes():
    comparison = RepositorySnapshotComparison(
        "/a",
        "/b",
        "same",
        "same",
    )
    assert comparison.has_changes is False


def test_comparison_004_has_changes():
    comparison = RepositorySnapshotComparison(
        "/a",
        "/b",
        "one",
        "two",
    )
    assert comparison.has_changes is True


def test_comparison_005_change_counts():
    comparison = RepositorySnapshotComparison(
        "/a",
        "/b",
        "one",
        "two",
        [
            RepositorySnapshotMetricChange(
                "files",
                1,
                2,
                1,
                "increased",
            ),
            RepositorySnapshotMetricChange(
                "symbols",
                3,
                2,
                -1,
                "decreased",
            ),
        ],
    )

    assert comparison.increased_metric_count == 1
    assert comparison.decreased_metric_count == 1


def test_comparison_006_changed_metric_names():
    comparison = RepositorySnapshotComparison(
        "/a",
        "/b",
        "one",
        "two",
        [
            RepositorySnapshotMetricChange(
                "files",
                1,
                2,
                1,
                "increased",
            ),
            RepositorySnapshotMetricChange(
                "symbols",
                3,
                3,
                0,
                "unchanged",
            ),
        ],
    )

    assert comparison.changed_metric_names == ["files"]


def test_comparison_007_identical_snapshots():
    snapshot = make_snapshot(
        "/repo",
        "same",
        [
            RepositoryIntelligenceSnapshotMetric(
                "files",
                2,
                "healthy",
            )
        ],
    )

    comparison = (
        RepositorySnapshotComparisonBuilder()
        .compare_snapshots(snapshot, snapshot)
    )

    assert comparison.has_changes is False


def test_comparison_008_increased_metric():
    baseline = make_snapshot(
        "/a",
        "one",
        [
            RepositoryIntelligenceSnapshotMetric(
                "files",
                2,
                "healthy",
            )
        ],
    )
    candidate = make_snapshot(
        "/b",
        "two",
        [
            RepositoryIntelligenceSnapshotMetric(
                "files",
                3,
                "healthy",
            )
        ],
    )

    comparison = (
        RepositorySnapshotComparisonBuilder()
        .compare_snapshots(baseline, candidate)
    )

    assert comparison.increased_metric_count == 1


def test_comparison_009_added_metric():
    baseline = make_snapshot("/a", "one", [])
    candidate = make_snapshot(
        "/b",
        "two",
        [
            RepositoryIntelligenceSnapshotMetric(
                "files",
                3,
                "healthy",
            )
        ],
    )

    comparison = (
        RepositorySnapshotComparisonBuilder()
        .compare_snapshots(baseline, candidate)
    )

    assert comparison.added_metric_count == 1


def test_comparison_010_removed_metric():
    baseline = make_snapshot(
        "/a",
        "one",
        [
            RepositoryIntelligenceSnapshotMetric(
                "files",
                3,
                "healthy",
            )
        ],
    )
    candidate = make_snapshot("/b", "two", [])

    comparison = (
        RepositorySnapshotComparisonBuilder()
        .compare_snapshots(baseline, candidate)
    )

    assert comparison.removed_metric_count == 1


def test_comparison_011_node_delta():
    baseline = make_snapshot(
        "/a",
        "one",
        node_count=10,
    )
    candidate = make_snapshot(
        "/b",
        "two",
        node_count=14,
    )

    comparison = (
        RepositorySnapshotComparisonBuilder()
        .compare_snapshots(baseline, candidate)
    )

    assert comparison.node_delta == 4


def test_comparison_012_real_repositories_identical(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(tmp_path / "candidate")

    comparison = RepositorySnapshotComparisonBuilder().compare(
        baseline,
        candidate,
    )

    assert comparison.has_changes is False


def test_comparison_013_real_repositories_changed(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    comparison = RepositorySnapshotComparisonBuilder().compare(
        baseline,
        candidate,
    )

    assert comparison.has_changes is True


def test_comparison_014_missing_baseline(tmp_path):
    candidate = make_repo(tmp_path / "candidate")

    try:
        RepositorySnapshotComparisonBuilder().compare(
            tmp_path / "missing",
            candidate,
        )
        assert False
    except FileNotFoundError:
        assert True


def test_comparison_015_summary_identical():
    summary = RepositorySnapshotComparisonSummaryBuilder().build(
        RepositorySnapshotComparison(
            "/a",
            "/b",
            "same",
            "same",
        )
    )

    assert summary.outcome == "identical"


def test_comparison_016_summary_changed():
    summary = RepositorySnapshotComparisonSummaryBuilder().build(
        RepositorySnapshotComparison(
            "/a",
            "/b",
            "one",
            "two",
            [
                RepositorySnapshotMetricChange(
                    "files",
                    1,
                    2,
                    1,
                    "increased",
                )
            ],
        )
    )

    assert summary.outcome == "changed"


def test_comparison_017_summary_attention():
    summary = RepositorySnapshotComparisonSummaryBuilder().build(
        RepositorySnapshotComparison(
            "/a",
            "/b",
            "one",
            "two",
            [
                RepositorySnapshotMetricChange(
                    "files",
                    2,
                    1,
                    -1,
                    "decreased",
                )
            ],
        )
    )

    assert summary.outcome == "attention_required"


def test_comparison_018_serialize():
    response = serialize_repository_snapshot_comparison(
        RepositorySnapshotComparison(
            "/a",
            "/b",
            "one",
            "two",
            [
                RepositorySnapshotMetricChange(
                    "files",
                    1,
                    2,
                    1,
                    "increased",
                )
            ],
            node_delta=1,
        )
    )

    assert response.has_changes is True
    assert response.node_delta == 1


def test_comparison_019_api_identical(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(tmp_path / "candidate")

    response = client.post(
        "/api/v1/repository-snapshot-comparison",
        json={
            "baseline_repository_path": str(baseline),
            "candidate_repository_path": str(candidate),
        },
    )

    assert response.status_code == 200
    assert response.json()["has_changes"] is False


def test_comparison_020_api_changed(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    response = client.post(
        "/api/v1/repository-snapshot-comparison",
        json={
            "baseline_repository_path": str(baseline),
            "candidate_repository_path": str(candidate),
        },
    )

    assert response.status_code == 200
    assert response.json()["has_changes"] is True


def test_comparison_021_api_missing_path(tmp_path):
    candidate = make_repo(tmp_path / "candidate")

    response = client.post(
        "/api/v1/repository-snapshot-comparison",
        json={
            "baseline_repository_path": str(
                tmp_path / "missing"
            ),
            "candidate_repository_path": str(candidate),
        },
    )

    assert response.status_code == 400


def test_comparison_022_api_empty_path():
    response = client.post(
        "/api/v1/repository-snapshot-comparison",
        json={
            "baseline_repository_path": "",
            "candidate_repository_path": "",
        },
    )

    assert response.status_code == 422


def test_comparison_023_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-snapshot-comparison"
        in paths
    )


def test_comparison_024_route_supports_post():
    route = next(
        route
        for route in app.routes
        if (
            route.path
            == "/api/v1/repository-snapshot-comparison"
        )
    )

    assert "POST" in route.methods
