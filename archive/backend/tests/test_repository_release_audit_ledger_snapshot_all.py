import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_audit_ledger_snapshot import (
    serialize_release_audit_ledger_snapshot,
)
from app.connectors.repository.repository_release_audit_bundle import (
    RepositoryReleaseAuditBundleBuilder,
)
from app.connectors.repository.repository_release_audit_ledger import (
    RepositoryReleaseAuditLedgerBuilder,
)
from app.connectors.repository.repository_release_audit_ledger_snapshot import (
    RepositoryReleaseAuditLedgerSnapshot,
    RepositoryReleaseAuditLedgerSnapshotBuilder,
    RepositoryReleaseAuditLedgerSnapshotEntry,
    verify_release_audit_ledger_snapshot,
)
from app.connectors.repository.repository_release_audit_ledger_snapshot_summary import (
    RepositoryReleaseAuditLedgerSnapshotSummaryBuilder,
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


def make_ledger_json(tmp_path: Path) -> str:
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

    ledger = RepositoryReleaseAuditLedgerBuilder().build(
        [bundle.as_json()]
    )

    return ledger.as_json()


def make_snapshot(
    accepted: bool = True,
):
    entry = RepositoryReleaseAuditLedgerSnapshotEntry(
        sequence=1,
        bundle_id="a" * 64,
        repository_name="repo",
        accepted=accepted,
        entry_hash="b" * 64,
    )

    provisional = RepositoryReleaseAuditLedgerSnapshot(
        schema_version="1.0",
        snapshot_id="",
        ledger_id="c" * 64,
        ledger_integrity_valid=True,
        ledger_chain_valid=True,
        ledger_accepted=accepted,
        entry_count=1,
        accepted_entry_count=1 if accepted else 0,
        rejected_entry_count=0 if accepted else 1,
        latest_entry_hash=entry.entry_hash,
        repository_names=["repo"],
        entries=[entry],
        issue_codes=[] if accepted else [
            "ledger_contains_rejections"
        ],
    )

    import hashlib

    snapshot_id = hashlib.sha256(
        provisional.canonical_json().encode("utf-8")
    ).hexdigest()

    return RepositoryReleaseAuditLedgerSnapshot(
        schema_version=provisional.schema_version,
        snapshot_id=snapshot_id,
        ledger_id=provisional.ledger_id,
        ledger_integrity_valid=(
            provisional.ledger_integrity_valid
        ),
        ledger_chain_valid=provisional.ledger_chain_valid,
        ledger_accepted=provisional.ledger_accepted,
        entry_count=provisional.entry_count,
        accepted_entry_count=(
            provisional.accepted_entry_count
        ),
        rejected_entry_count=(
            provisional.rejected_entry_count
        ),
        latest_entry_hash=provisional.latest_entry_hash,
        repository_names=provisional.repository_names,
        entries=provisional.entries,
        issue_codes=provisional.issue_codes,
    )


def test_snapshot_001_accepted():
    assert make_snapshot(True).accepted is True


def test_snapshot_002_rejected():
    assert make_snapshot(False).rejected is True


def test_snapshot_003_repository_count():
    assert make_snapshot().repository_count == 1


def test_snapshot_004_issue_count():
    assert make_snapshot(False).issue_count == 1


def test_snapshot_005_status():
    assert make_snapshot().status == (
        "ledger_snapshot_accepted"
    )


def test_snapshot_006_valid():
    assert verify_release_audit_ledger_snapshot(
        make_snapshot()
    ) is True


def test_snapshot_007_json():
    payload = json.loads(make_snapshot().as_json())

    assert payload["accepted"] is True
    assert len(payload["snapshot_id"]) == 64


def test_snapshot_008_markdown():
    markdown = make_snapshot().as_markdown()

    assert (
        "# Repository Release Audit Ledger Snapshot"
        in markdown
    )


def test_snapshot_009_real_ledger(tmp_path):
    snapshot = (
        RepositoryReleaseAuditLedgerSnapshotBuilder()
        .build(make_ledger_json(tmp_path))
    )

    assert snapshot.accepted is True
    assert snapshot.entry_count == 1


def test_snapshot_010_latest_hash(tmp_path):
    snapshot = (
        RepositoryReleaseAuditLedgerSnapshotBuilder()
        .build(make_ledger_json(tmp_path))
    )

    assert len(snapshot.latest_entry_hash) == 64


def test_snapshot_011_repository_names(tmp_path):
    snapshot = (
        RepositoryReleaseAuditLedgerSnapshotBuilder()
        .build(make_ledger_json(tmp_path))
    )

    assert snapshot.repository_names == ["repo"]


def test_snapshot_012_tampered_ledger(tmp_path):
    payload = json.loads(make_ledger_json(tmp_path))
    payload["entries"][0]["repository_name"] = "tampered"

    snapshot = (
        RepositoryReleaseAuditLedgerSnapshotBuilder()
        .build(
            json.dumps(payload),
            require_all_accepted=False,
        )
    )

    assert snapshot.rejected is True
    assert snapshot.issue_count > 0


def test_snapshot_013_summary_accepted():
    summary = (
        RepositoryReleaseAuditLedgerSnapshotSummaryBuilder()
        .build(make_snapshot())
    )

    assert summary.outcome == (
        "ledger_snapshot_accepted"
    )


def test_snapshot_014_summary_rejected():
    summary = (
        RepositoryReleaseAuditLedgerSnapshotSummaryBuilder()
        .build(make_snapshot(False))
    )

    assert summary.action_required is True


def test_snapshot_015_serialize():
    response = serialize_release_audit_ledger_snapshot(
        make_snapshot()
    )

    assert response.accepted is True
    assert response.snapshot_valid is True


def test_snapshot_016_api(tmp_path):
    response = client.post(
        "/api/v1/repository-release-audit-ledger-snapshot",
        json={
            "ledger_json": make_ledger_json(tmp_path)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["snapshot_valid"] is True


def test_snapshot_017_api_tampered(tmp_path):
    payload = json.loads(make_ledger_json(tmp_path))
    payload["entries"][0]["repository_name"] = "tampered"

    response = client.post(
        "/api/v1/repository-release-audit-ledger-snapshot",
        json={
            "ledger_json": json.dumps(payload),
            "require_all_accepted": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["rejected"] is True


def test_snapshot_018_api_invalid_json():
    response = client.post(
        "/api/v1/repository-release-audit-ledger-snapshot",
        json={"ledger_json": "{invalid"},
    )

    assert response.status_code == 400


def test_snapshot_019_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-audit-ledger-snapshot"
        in paths
    )


def test_snapshot_020_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path
        == "/api/v1/repository-release-audit-ledger-snapshot"
    )

    assert "POST" in route.methods
