import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_audit_ledger_progression_gate import (
    serialize_ledger_progression_gate,
)
from app.connectors.repository.repository_release_audit_bundle import (
    RepositoryReleaseAuditBundleBuilder,
)
from app.connectors.repository.repository_release_audit_ledger import (
    RepositoryReleaseAuditLedgerBuilder,
)
from app.connectors.repository.repository_release_audit_ledger_progression_gate import (
    RepositoryReleaseAuditLedgerProgressionGateEvaluator,
)
from app.connectors.repository.repository_release_audit_ledger_progression_gate_summary import (
    RepositoryReleaseAuditLedgerProgressionGateSummaryBuilder,
)
from app.connectors.repository.repository_release_audit_ledger_snapshot import (
    RepositoryReleaseAuditLedgerSnapshotBuilder,
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


def test_gate_001_safe_progression_passes(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(baseline, candidate)
    )

    assert gate.passed is True


def test_gate_002_exit_code_passed(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(baseline, candidate)
    )

    assert gate.exit_code == 0


def test_gate_003_unchanged_allowed(tmp_path):
    baseline, _ = make_snapshots(tmp_path)

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(
            baseline,
            baseline,
            allow_unchanged=True,
        )
    )

    assert gate.passed is True
    assert gate.status == "unchanged_passed"


def test_gate_004_unchanged_blocked(tmp_path):
    baseline, _ = make_snapshots(tmp_path)

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(
            baseline,
            baseline,
            allow_unchanged=False,
        )
    )

    assert gate.blocked is True
    assert "unchanged_snapshot_not_allowed" in (
        gate.reason_codes
    )


def test_gate_005_reverse_blocks(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(candidate, baseline)
    )

    assert gate.blocked is True
    assert "ledger_history_rewritten" in gate.reason_codes


def test_gate_006_tampered_candidate_blocks(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    payload = json.loads(candidate)
    payload["entries"][0]["repository_name"] = "tampered"

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(
            baseline,
            json.dumps(payload),
        )
    )

    assert gate.blocked is True
    assert "candidate_snapshot_invalid" in (
        gate.reason_codes
    )


def test_gate_007_reason_count(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    payload = json.loads(candidate)
    payload["entries"][0]["repository_name"] = "tampered"

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(
            baseline,
            json.dumps(payload),
        )
    )

    assert gate.reason_count > 0


def test_gate_008_critical_count(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    payload = json.loads(candidate)
    payload["entries"][0]["repository_name"] = "tampered"

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(
            baseline,
            json.dumps(payload),
        )
    )

    assert gate.critical_reason_count > 0


def test_gate_009_added_bundle(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(baseline, candidate)
    )

    assert len(gate.comparison.added_bundle_ids) == 1


def test_gate_010_no_removed_bundle(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(baseline, candidate)
    )

    assert gate.comparison.removed_bundle_ids == []


def test_gate_011_summary_passed(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(baseline, candidate)
    )

    summary = (
        RepositoryReleaseAuditLedgerProgressionGateSummaryBuilder()
        .build(gate)
    )

    assert summary.outcome == "ledger_progression_passed"


def test_gate_012_summary_unchanged(tmp_path):
    baseline, _ = make_snapshots(tmp_path)

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(baseline, baseline)
    )

    summary = (
        RepositoryReleaseAuditLedgerProgressionGateSummaryBuilder()
        .build(gate)
    )

    assert summary.outcome == "ledger_unchanged_passed"


def test_gate_013_summary_blocked(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(candidate, baseline)
    )

    summary = (
        RepositoryReleaseAuditLedgerProgressionGateSummaryBuilder()
        .build(gate)
    )

    assert summary.action_required is True


def test_gate_014_serialize(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    gate = (
        RepositoryReleaseAuditLedgerProgressionGateEvaluator()
        .evaluate(baseline, candidate)
    )

    response = serialize_ledger_progression_gate(gate)

    assert response.passed is True
    assert response.entry_count_delta == 1


def test_gate_015_api_passes(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    response = client.post(
        "/api/v1/repository-release-audit-ledger-progression-gate",
        json={
            "baseline_snapshot_json": baseline,
            "candidate_snapshot_json": candidate,
        },
    )

    assert response.status_code == 200
    assert response.json()["passed"] is True
    assert response.json()["exit_code"] == 0


def test_gate_016_api_blocks_reverse(tmp_path):
    baseline, candidate = make_snapshots(tmp_path)

    response = client.post(
        "/api/v1/repository-release-audit-ledger-progression-gate",
        json={
            "baseline_snapshot_json": candidate,
            "candidate_snapshot_json": baseline,
        },
    )

    assert response.status_code == 200
    assert response.json()["blocked"] is True


def test_gate_017_api_invalid_json(tmp_path):
    baseline, _ = make_snapshots(tmp_path)

    response = client.post(
        "/api/v1/repository-release-audit-ledger-progression-gate",
        json={
            "baseline_snapshot_json": baseline,
            "candidate_snapshot_json": "{invalid",
        },
    )

    assert response.status_code == 400


def test_gate_018_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-audit-ledger-progression-gate"
        in paths
    )


def test_gate_019_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path
        == "/api/v1/repository-release-audit-ledger-progression-gate"
    )

    assert "POST" in route.methods
