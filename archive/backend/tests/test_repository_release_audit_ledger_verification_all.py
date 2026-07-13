import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_audit_ledger_verification import (
    serialize_release_audit_ledger_verification,
)
from app.connectors.repository.repository_release_audit_bundle import (
    RepositoryReleaseAuditBundleBuilder,
)
from app.connectors.repository.repository_release_audit_ledger import (
    RepositoryReleaseAuditLedgerBuilder,
)
from app.connectors.repository.repository_release_audit_ledger_verification import (
    RepositoryReleaseAuditLedgerDocumentVerification,
    RepositoryReleaseAuditLedgerDocumentVerifier,
    RepositoryReleaseAuditLedgerVerificationIssue,
)
from app.connectors.repository.repository_release_audit_ledger_verification_summary import (
    RepositoryReleaseAuditLedgerVerificationSummaryBuilder,
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


def make_verification(
    accepted: bool = True,
    integrity_valid: bool = True,
    chain_valid: bool = True,
    issues=None,
):
    return RepositoryReleaseAuditLedgerDocumentVerification(
        ledger_id="a" * 64,
        schema_version="1.0",
        integrity_valid=integrity_valid,
        chain_valid=chain_valid,
        entry_count=1,
        accepted_entry_count=1 if accepted else 0,
        rejected_entry_count=0 if accepted else 1,
        issues=issues or [],
    )


def test_ledger_verification_001_valid():
    assert make_verification().valid is True


def test_ledger_verification_002_accepted():
    assert make_verification().accepted is True


def test_ledger_verification_003_rejected():
    assert make_verification(
        accepted=False
    ).rejected is True


def test_ledger_verification_004_issue_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditLedgerVerificationIssue(
                "issue",
                "error",
                "Message.",
            )
        ]
    )

    assert verification.issue_count == 1


def test_ledger_verification_005_critical_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditLedgerVerificationIssue(
                "issue",
                "critical",
                "Message.",
                1,
            )
        ]
    )

    assert verification.critical_issue_count == 1


def test_ledger_verification_006_invalid_sequences():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditLedgerVerificationIssue(
                "issue",
                "critical",
                "Message.",
                2,
            ),
            RepositoryReleaseAuditLedgerVerificationIssue(
                "other",
                "critical",
                "Message.",
                1,
            ),
        ]
    )

    assert verification.invalid_entry_sequences == [1, 2]


def test_ledger_verification_007_status():
    assert make_verification().status == (
        "release_audit_ledger_accepted"
    )


def test_ledger_verification_008_real_ledger(tmp_path):
    verification = (
        RepositoryReleaseAuditLedgerDocumentVerifier()
        .verify_json(make_ledger_json(tmp_path))
    )

    assert verification.accepted is True
    assert verification.integrity_valid is True
    assert verification.chain_valid is True


def test_ledger_verification_009_tampered_entry(tmp_path):
    payload = json.loads(make_ledger_json(tmp_path))
    payload["entries"][0]["repository_name"] = "tampered"

    verification = (
        RepositoryReleaseAuditLedgerDocumentVerifier()
        .verify_json(json.dumps(payload))
    )

    assert verification.valid is False
    assert "entry_integrity_failure" in (
        verification.issue_codes
    )


def test_ledger_verification_010_broken_chain(tmp_path):
    payload = json.loads(make_ledger_json(tmp_path))
    payload["entries"][0]["previous_entry_hash"] = "f" * 64

    verification = (
        RepositoryReleaseAuditLedgerDocumentVerifier()
        .verify_json(json.dumps(payload))
    )

    assert verification.chain_valid is False
    assert "broken_chain_link" in verification.issue_codes


def test_ledger_verification_011_bad_schema(tmp_path):
    payload = json.loads(make_ledger_json(tmp_path))
    payload["schema_version"] = "999"

    verification = (
        RepositoryReleaseAuditLedgerDocumentVerifier()
        .verify_json(json.dumps(payload))
    )

    assert "unsupported_schema_version" in (
        verification.issue_codes
    )


def test_ledger_verification_012_ledger_mismatch(
    tmp_path,
):
    verification = (
        RepositoryReleaseAuditLedgerDocumentVerifier()
        .verify_json(
            make_ledger_json(tmp_path),
            expected_ledger_id="different",
        )
    )

    assert "ledger_id_mismatch" in (
        verification.issue_codes
    )


def test_ledger_verification_013_bundle_sequence(
    tmp_path,
):
    payload = json.loads(make_ledger_json(tmp_path))

    verification = (
        RepositoryReleaseAuditLedgerDocumentVerifier()
        .verify_json(
            json.dumps(payload),
            expected_bundle_ids=[
                payload["entries"][0]["bundle_id"]
            ],
        )
    )

    assert (
        "bundle_sequence_mismatch"
        not in verification.issue_codes
    )


def test_ledger_verification_014_invalid_json():
    try:
        RepositoryReleaseAuditLedgerDocumentVerifier().verify_json(
            "{invalid"
        )
        assert False
    except ValueError:
        assert True


def test_ledger_verification_015_missing_fields():
    try:
        RepositoryReleaseAuditLedgerDocumentVerifier().verify_json(
            "{}"
        )
        assert False
    except ValueError:
        assert True


def test_ledger_verification_016_summary_accepted():
    summary = (
        RepositoryReleaseAuditLedgerVerificationSummaryBuilder()
        .build(make_verification())
    )

    assert summary.outcome == (
        "release_audit_ledger_accepted"
    )


def test_ledger_verification_017_summary_critical():
    verification = make_verification(
        integrity_valid=False,
        issues=[
            RepositoryReleaseAuditLedgerVerificationIssue(
                "integrity",
                "critical",
                "Failed.",
            )
        ],
    )

    summary = (
        RepositoryReleaseAuditLedgerVerificationSummaryBuilder()
        .build(verification)
    )

    assert summary.outcome == (
        "release_audit_ledger_rejected_critical"
    )


def test_ledger_verification_018_serialize():
    response = serialize_release_audit_ledger_verification(
        make_verification()
    )

    assert response.accepted is True
    assert response.issue_count == 0


def test_ledger_verification_019_api_accepts(tmp_path):
    response = client.post(
        "/api/v1/repository-release-audit-ledger-verification",
        json={
            "ledger_json": make_ledger_json(tmp_path)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_ledger_verification_020_api_tampered(tmp_path):
    payload = json.loads(make_ledger_json(tmp_path))
    payload["entries"][0]["repository_name"] = "tampered"

    response = client.post(
        "/api/v1/repository-release-audit-ledger-verification",
        json={
            "ledger_json": json.dumps(payload)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_ledger_verification_021_api_invalid_json():
    response = client.post(
        "/api/v1/repository-release-audit-ledger-verification",
        json={"ledger_json": "{invalid"},
    )

    assert response.status_code == 400


def test_ledger_verification_022_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-audit-ledger-verification"
        in paths
    )


def test_ledger_verification_023_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path
        == "/api/v1/repository-release-audit-ledger-verification"
    )

    assert "POST" in route.methods
