import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_audit_ledger_snapshot_comparison import (
    serialize_ledger_snapshot_comparison,
)
from app.connectors.repository.repository_release_audit_bundle import (
    RepositoryReleaseAuditBundleBuilder,
)
from app.connectors.repository.repository_release_audit_ledger import (
    RepositoryReleaseAuditLedgerBuilder,
)
from app.connectors.repository.repository_release_audit_ledger_snapshot import (
    RepositoryReleaseAuditLedgerSnapshotBuilder,
)
from app.connectors.repository.repository_release_audit_ledger_snapshot_comparison import (
    RepositoryReleaseAuditLedgerSnapshotComparisonBuilder,
)
from app.connectors.repository.repository_release_audit_ledger_snapshot_comparison_summary import (
    RepositoryReleaseAuditLedgerSnapshotComparisonSummaryBuilder,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaselineBuilder,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)
from app.main import app

client = TestClient(app)


def make_repo(root: Path) -> Path:
    root.mkdir()

    root.joinpath("requirements.txt").write_text(
        "fastapi\npytest\n",
        encoding="utf-8",
    )

    root.joinpath("app.py").write_text(
        "import os\n"
        "class Worker:\n"
        "    def run(self):\n"
        "        return os.getcwd()\n",
        encoding="utf-8",
    )

    return root


def make_bundle_json(tmp_path: Path) -> str:
    repo = make_repo(tmp_path / "repo")

    baseline = RepositorySnapshotBaselineBuilder().build(
        repo
    )

    bundle = RepositoryReleaseAuditBundleBuilder().build(
        repository_path=str(repo),
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    return bundle.as_json()


def make_snapshots(
    tmp_path: Path,
) -> tuple[str, str]:
    bundle_json = make_bundle_json(tmp_path)

    baseline_ledger = (
        RepositoryReleaseAuditLedgerBuilder()
        .build([bundle_json])
    )

    candidate_ledger = (
        RepositoryReleaseAuditLedgerBuilder()
        .build([bundle_json, bundle_json])
    )

    baseline_snapshot = (
        RepositoryReleaseAuditLedgerSnapshotBuilder()
        .build(baseline_ledger.as_json())
    )

    candidate_snapshot = (
        RepositoryReleaseAuditLedgerSnapshotBuilder()
        .build(candidate_ledger.as_json())
    )

    return (
        baseline_snapshot.as_json(),
        candidate_snapshot.as_json(),
    )


def test_comparison_001_identical(tmp_path):
    baseline, _ = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, baseline)
    )

    assert comparison.snapshots_identical is True


def test_comparison_002_changed(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, candidate)
    )

    assert comparison.changed is True


def test_comparison_003_entry_delta(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, candidate)
    )

    assert comparison.entry_count_delta == 1


def test_comparison_004_append_only(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, candidate)
    )

    assert comparison.append_only is True


def test_comparison_005_safe_progression(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, candidate)
    )

    assert comparison.safe_progression is True


def test_comparison_006_added_bundle(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, candidate)
    )

    assert len(comparison.added_bundle_ids) == 1


def test_comparison_007_no_removed_bundle(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, candidate)
    )

    assert comparison.removed_bundle_ids == []


def test_comparison_008_reverse_not_append_only(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(candidate, baseline)
    )

    assert comparison.append_only is False
    assert comparison.history_rewritten is True


def test_comparison_009_tampered_history(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    payload = json.loads(candidate)
    payload["entries"][0]["entry_hash"] = "f" * 64

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(
            baseline,
            json.dumps(payload),
        )
    )

    assert comparison.history_rewritten is True


def test_comparison_010_status_unchanged(tmp_path):
    baseline, _ = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, baseline)
    )

    assert comparison.status == "unchanged"


def test_comparison_011_status_safe(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, candidate)
    )

    assert comparison.status == "safe_progression"


def test_comparison_012_summary_unchanged(tmp_path):
    baseline, _ = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, baseline)
    )

    summary = (
        RepositoryReleaseAuditLedgerSnapshotComparisonSummaryBuilder()
        .build(comparison)
    )

    assert summary.outcome == (
        "ledger_snapshot_unchanged"
    )


def test_comparison_013_summary_safe(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, candidate)
    )

    summary = (
        RepositoryReleaseAuditLedgerSnapshotComparisonSummaryBuilder()
        .build(comparison)
    )

    assert summary.outcome == (
        "ledger_safe_progression"
    )


def test_comparison_014_serialize(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    comparison = (
        RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
        .build(baseline, candidate)
    )

    response = serialize_ledger_snapshot_comparison(
        comparison
    )

    assert response.safe_progression is True
    assert response.entry_count_delta == 1


def test_comparison_015_api(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    response = client.post(
        "/api/v1/repository-release-audit-ledger-snapshot-comparison",
        json={
            "baseline_snapshot_json": baseline,
            "candidate_snapshot_json": candidate,
        },
    )

    assert response.status_code == 200
    assert response.json()["safe_progression"] is True
    assert response.json()["entry_count_delta"] == 1


def test_comparison_016_api_identical(tmp_path):
    baseline, _ = make_snapshots(tmp_path)

    response = client.post(
        "/api/v1/repository-release-audit-ledger-snapshot-comparison",
        json={
            "baseline_snapshot_json": baseline,
            "candidate_snapshot_json": baseline,
        },
    )

    assert response.status_code == 200
    assert response.json()["snapshots_identical"] is True


def test_comparison_017_api_invalid_json(tmp_path):
    baseline, _ = make_snapshots(tmp_path)

    response = client.post(
        "/api/v1/repository-release-audit-ledger-snapshot-comparison",
        json={
            "baseline_snapshot_json": baseline,
            "candidate_snapshot_json": "{invalid",
        },
    )

    assert response.status_code == 400


def test_comparison_018_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-audit-ledger-snapshot-comparison"
        in paths
    )


def test_comparison_019_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path
        == "/api/v1/repository-release-audit-ledger-snapshot-comparison"
    )

    assert "POST" in route.methods
