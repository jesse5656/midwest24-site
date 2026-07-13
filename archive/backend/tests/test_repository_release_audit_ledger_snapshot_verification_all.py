import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_audit_ledger_snapshot_verification import (
    serialize_ledger_snapshot_verification,
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
from app.connectors.repository.repository_release_audit_ledger_snapshot_verification import (
    RepositoryReleaseAuditLedgerSnapshotVerification,
    RepositoryReleaseAuditLedgerSnapshotVerificationIssue,
    RepositoryReleaseAuditLedgerSnapshotVerifier,
)
from app.connectors.repository.repository_release_audit_ledger_snapshot_verification_summary import (
    RepositoryReleaseAuditLedgerSnapshotVerificationSummaryBuilder,
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


def make_snapshot_json(tmp_path: Path) -> str:
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

    snapshot = (
        RepositoryReleaseAuditLedgerSnapshotBuilder()
        .build(ledger.as_json())
    )

    return snapshot.as_json()


def make_verification(
    accepted: bool = True,
    integrity_valid: bool = True,
    issues=None,
):
    return RepositoryReleaseAuditLedgerSnapshotVerification(
        snapshot_id="a" * 64,
        ledger_id="b" * 64,
        schema_version="1.0",
        snapshot_accepted=accepted,
        integrity_valid=integrity_valid,
        entry_count=1,
        accepted_entry_count=1 if accepted else 0,
        rejected_entry_count=0 if accepted else 1,
        repository_count=1,
        issues=issues or [],
    )


def test_snapshot_verification_001_valid():
    assert make_verification().valid is True


def test_snapshot_verification_002_accepted():
    assert make_verification().accepted is True


def test_snapshot_verification_003_rejected():
    assert make_verification(
        accepted=False
    ).rejected is True


def test_snapshot_verification_004_issue_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                "issue",
                "error",
                "Message.",
            )
        ]
    )

    assert verification.issue_count == 1


def test_snapshot_verification_005_critical_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                "issue",
                "critical",
                "Message.",
                1,
            )
        ]
    )

    assert verification.critical_issue_count == 1


def test_snapshot_verification_006_sequences():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                "issue",
                "critical",
                "Message.",
                2,
            ),
            RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                "other",
                "critical",
                "Message.",
                1,
            ),
        ]
    )

    assert verification.invalid_entry_sequences == [1, 2]


def test_snapshot_verification_007_status():
    assert make_verification().status == (
        "ledger_snapshot_accepted"
    )


def test_snapshot_verification_008_real_snapshot(tmp_path):
    verification = (
        RepositoryReleaseAuditLedgerSnapshotVerifier()
        .verify_json(make_snapshot_json(tmp_path))
    )

    assert verification.accepted is True
    assert verification.integrity_valid is True


def test_snapshot_verification_009_tampered(tmp_path):
    payload = json.loads(make_snapshot_json(tmp_path))
    payload["entries"][0]["repository_name"] = "tampered"

    verification = (
        RepositoryReleaseAuditLedgerSnapshotVerifier()
        .verify_json(json.dumps(payload))
    )

    assert verification.valid is False
    assert "snapshot_integrity_failure" in (
        verification.issue_codes
    )


def test_snapshot_verification_010_count_mismatch(tmp_path):
    payload = json.loads(make_snapshot_json(tmp_path))
    payload["entry_count"] = 99

    verification = (
        RepositoryReleaseAuditLedgerSnapshotVerifier()
        .verify_json(json.dumps(payload))
    )

    assert "entry_count_mismatch" in (
        verification.issue_codes
    )


def test_snapshot_verification_011_latest_hash_mismatch(
    tmp_path,
):
    payload = json.loads(make_snapshot_json(tmp_path))
    payload["latest_entry_hash"] = "f" * 64

    verification = (
        RepositoryReleaseAuditLedgerSnapshotVerifier()
        .verify_json(json.dumps(payload))
    )

    assert "latest_entry_hash_mismatch" in (
        verification.issue_codes
    )


def test_snapshot_verification_012_bad_schema(tmp_path):
    payload = json.loads(make_snapshot_json(tmp_path))
    payload["schema_version"] = "999"

    verification = (
        RepositoryReleaseAuditLedgerSnapshotVerifier()
        .verify_json(json.dumps(payload))
    )

    assert "unsupported_schema_version" in (
        verification.issue_codes
    )


def test_snapshot_verification_013_expected_ledger(
    tmp_path,
):
    payload = json.loads(make_snapshot_json(tmp_path))

    verification = (
        RepositoryReleaseAuditLedgerSnapshotVerifier()
        .verify_json(
            json.dumps(payload),
            expected_ledger_id=payload["ledger_id"],
        )
    )

    assert "ledger_id_mismatch" not in (
        verification.issue_codes
    )


def test_snapshot_verification_014_ledger_mismatch(
    tmp_path,
):
    verification = (
        RepositoryReleaseAuditLedgerSnapshotVerifier()
        .verify_json(
            make_snapshot_json(tmp_path),
            expected_ledger_id="different",
        )
    )

    assert "ledger_id_mismatch" in (
        verification.issue_codes
    )


def test_snapshot_verification_015_invalid_json():
    try:
        RepositoryReleaseAuditLedgerSnapshotVerifier().verify_json(
            "{invalid"
        )
        assert False
    except ValueError:
        assert True


def test_snapshot_verification_016_missing_fields():
    try:
        RepositoryReleaseAuditLedgerSnapshotVerifier().verify_json(
            "{}"
        )
        assert False
    except ValueError:
        assert True


def test_snapshot_verification_017_summary_accepted():
    summary = (
        RepositoryReleaseAuditLedgerSnapshotVerificationSummaryBuilder()
        .build(make_verification())
    )

    assert summary.outcome == "ledger_snapshot_accepted"


def test_snapshot_verification_018_summary_critical():
    verification = make_verification(
        integrity_valid=False,
        issues=[
            RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                "integrity",
                "critical",
                "Failed.",
            )
        ],
    )

    summary = (
        RepositoryReleaseAuditLedgerSnapshotVerificationSummaryBuilder()
        .build(verification)
    )

    assert summary.outcome == (
        "ledger_snapshot_rejected_critical"
    )


def test_snapshot_verification_019_serialize():
    response = serialize_ledger_snapshot_verification(
        make_verification()
    )

    assert response.accepted is True
    assert response.issue_count == 0


def test_snapshot_verification_020_api_accepts(tmp_path):
    response = client.post(
        "/api/v1/repository-release-audit-ledger-snapshot-verification",
        json={
            "snapshot_json": make_snapshot_json(tmp_path)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_snapshot_verification_021_api_tampered(tmp_path):
    payload = json.loads(make_snapshot_json(tmp_path))
    payload["entries"][0]["repository_name"] = "tampered"

    response = client.post(
        "/api/v1/repository-release-audit-ledger-snapshot-verification",
        json={
            "snapshot_json": json.dumps(payload)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_snapshot_verification_022_api_invalid_json():
    response = client.post(
        "/api/v1/repository-release-audit-ledger-snapshot-verification",
        json={"snapshot_json": "{invalid"},
    )

    assert response.status_code == 400


def test_snapshot_verification_023_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-audit-ledger-snapshot-verification"
        in paths
    )


def test_snapshot_verification_024_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path
        == "/api/v1/repository-release-audit-ledger-snapshot-verification"
    )

    assert "POST" in route.methods
