from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_snapshot_baseline import (
    serialize_repository_snapshot_baseline,
    serialize_repository_snapshot_baseline_verification,
)
from app.connectors.repository.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshot,
    RepositoryIntelligenceSnapshotMetric,
)
from app.connectors.repository.repository_snapshot_baseline import (
    BASELINE_SCHEMA_VERSION,
    RepositorySnapshotBaseline,
    RepositorySnapshotBaselineBuilder,
    RepositorySnapshotBaselineMetric,
    RepositorySnapshotBaselineVerification,
    RepositorySnapshotBaselineVerifier,
    baseline_checksum,
)
from app.connectors.repository.repository_snapshot_baseline_summary import (
    RepositorySnapshotBaselineSummaryBuilder,
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
    fingerprint: str = "abc123",
):
    return RepositoryIntelligenceSnapshot(
        repository_path="/repo",
        repository_name="repo",
        metrics=[
            RepositoryIntelligenceSnapshotMetric(
                "files",
                2,
                "healthy",
            )
        ],
        node_count=10,
        edge_count=8,
        report_section_count=5,
        warning_count=0,
        critical_count=0,
        fingerprint=fingerprint,
    )


def make_baseline(
    fingerprint: str = "abc123",
):
    return RepositorySnapshotBaseline(
        schema_version=BASELINE_SCHEMA_VERSION,
        repository_name="repo",
        fingerprint=fingerprint,
        metrics=[
            RepositorySnapshotBaselineMetric(
                "files",
                2,
                "healthy",
            )
        ],
        node_count=10,
        edge_count=8,
        report_section_count=5,
        warning_count=0,
        critical_count=0,
    )


def test_baseline_001_metric_count():
    assert make_baseline().metric_count == 1


def test_baseline_002_metric_names():
    assert make_baseline().metric_names == ["files"]


def test_baseline_003_metric_value():
    assert make_baseline().metric_value("files") == 2


def test_baseline_004_metric_value_missing():
    assert make_baseline().metric_value("missing") is None


def test_baseline_005_is_healthy():
    assert make_baseline().is_healthy is True


def test_baseline_006_warning_not_healthy():
    baseline = RepositorySnapshotBaseline(
        schema_version=BASELINE_SCHEMA_VERSION,
        repository_name="repo",
        fingerprint="abc",
        warning_count=1,
    )
    assert baseline.is_healthy is False


def test_baseline_007_json_round_trip():
    baseline = make_baseline()
    restored = RepositorySnapshotBaseline.from_json(
        baseline.to_json()
    )
    assert restored == baseline


def test_baseline_008_json_is_deterministic():
    baseline = make_baseline()
    assert baseline.to_json() == baseline.to_json()


def test_baseline_009_checksum_length():
    assert len(baseline_checksum(make_baseline())) == 64


def test_baseline_010_builder_from_snapshot():
    baseline = RepositorySnapshotBaselineBuilder().from_snapshot(
        make_snapshot()
    )
    assert baseline.fingerprint == "abc123"
    assert baseline.metric_count == 1


def test_baseline_011_builder_real_repo(tmp_path):
    baseline = RepositorySnapshotBaselineBuilder().build(
        make_repo(tmp_path / "repo")
    )
    assert len(baseline.fingerprint) == 64


def test_baseline_012_verify_identical_snapshot():
    verification = (
        RepositorySnapshotBaselineVerifier()
        .verify_snapshot(
            candidate=make_snapshot(),
            baseline=make_baseline(),
        )
    )
    assert verification.matches is True


def test_baseline_013_verify_fingerprint_mismatch():
    verification = (
        RepositorySnapshotBaselineVerifier()
        .verify_snapshot(
            candidate=make_snapshot("different"),
            baseline=make_baseline(),
        )
    )
    assert verification.matches is False
    assert verification.fingerprint_matches is False


def test_baseline_014_verify_metric_mismatch():
    candidate = RepositoryIntelligenceSnapshot(
        repository_path="/repo",
        repository_name="repo",
        metrics=[
            RepositoryIntelligenceSnapshotMetric(
                "files",
                3,
                "healthy",
            )
        ],
        node_count=10,
        edge_count=8,
        report_section_count=5,
        fingerprint="abc123",
    )

    verification = (
        RepositorySnapshotBaselineVerifier()
        .verify_snapshot(
            candidate=candidate,
            baseline=make_baseline(),
        )
    )

    assert verification.matches is False
    assert "metric_changed:files" in (
        verification.metric_differences
    )


def test_baseline_015_verify_real_repository(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    verification = RepositorySnapshotBaselineVerifier().verify(
        repository_path=repo,
        baseline=baseline,
    )

    assert verification.matches is True


def test_baseline_016_verify_changed_repository(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    verification = RepositorySnapshotBaselineVerifier().verify(
        repository_path=candidate_repo,
        baseline=baseline,
    )

    assert verification.matches is False


def test_baseline_017_summary_created():
    summary = RepositorySnapshotBaselineSummaryBuilder().build_baseline(
        make_baseline()
    )
    assert summary.outcome == "baseline_created"


def test_baseline_018_summary_match():
    verification = RepositorySnapshotBaselineVerification(
        baseline=make_baseline(),
        candidate=make_snapshot(),
        fingerprint_matches=True,
    )

    summary = (
        RepositorySnapshotBaselineSummaryBuilder()
        .build_verification(verification)
    )

    assert summary.outcome == "baseline_match"


def test_baseline_019_summary_mismatch():
    verification = RepositorySnapshotBaselineVerification(
        baseline=make_baseline(),
        candidate=make_snapshot("different"),
        fingerprint_matches=False,
        metric_differences=["metric_changed:files"],
    )

    summary = (
        RepositorySnapshotBaselineSummaryBuilder()
        .build_verification(verification)
    )

    assert summary.outcome == "baseline_mismatch"


def test_baseline_020_serialize_baseline():
    response = serialize_repository_snapshot_baseline(
        make_baseline()
    )
    assert response.metric_count == 1
    assert len(response.checksum) == 64


def test_baseline_021_serialize_verification():
    response = (
        serialize_repository_snapshot_baseline_verification(
            RepositorySnapshotBaselineVerification(
                baseline=make_baseline(),
                candidate=make_snapshot(),
                fingerprint_matches=True,
            )
        )
    )
    assert response.matches is True


def test_baseline_022_api_create(tmp_path):
    response = client.post(
        "/api/v1/repository-snapshot-baseline",
        json={
            "repository_path": str(
                make_repo(tmp_path / "repo")
            )
        },
    )

    assert response.status_code == 200
    assert len(
        response.json()["baseline"]["fingerprint"]
    ) == 64


def test_baseline_023_api_verify_match(tmp_path):
    repo = make_repo(tmp_path / "repo")

    created = client.post(
        "/api/v1/repository-snapshot-baseline",
        json={"repository_path": str(repo)},
    )

    response = client.post(
        "/api/v1/repository-snapshot-baseline/verify",
        json={
            "repository_path": str(repo),
            "baseline_json": created.json()["baseline_json"],
        },
    )

    assert response.status_code == 200
    assert response.json()["matches"] is True


def test_baseline_024_api_verify_changed(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    created = client.post(
        "/api/v1/repository-snapshot-baseline",
        json={
            "repository_path": str(baseline_repo)
        },
    )

    response = client.post(
        "/api/v1/repository-snapshot-baseline/verify",
        json={
            "repository_path": str(candidate_repo),
            "baseline_json": created.json()["baseline_json"],
        },
    )

    assert response.status_code == 200
    assert response.json()["matches"] is False


def test_baseline_025_api_invalid_json(tmp_path):
    repo = make_repo(tmp_path / "repo")

    response = client.post(
        "/api/v1/repository-snapshot-baseline/verify",
        json={
            "repository_path": str(repo),
            "baseline_json": "{invalid",
        },
    )

    assert response.status_code == 400


def test_baseline_026_api_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-snapshot-baseline",
        json={
            "repository_path": str(tmp_path / "missing")
        },
    )

    assert response.status_code == 400


def test_baseline_027_routes_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/repository-snapshot-baseline" in paths
    assert (
        "/api/v1/repository-snapshot-baseline/verify"
        in paths
    )


def test_baseline_028_routes_support_post():
    routes = {
        route.path: route
        for route in app.routes
    }

    assert "POST" in routes[
        "/api/v1/repository-snapshot-baseline"
    ].methods

    assert "POST" in routes[
        "/api/v1/repository-snapshot-baseline/verify"
    ].methods
