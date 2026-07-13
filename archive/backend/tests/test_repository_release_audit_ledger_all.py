from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_audit_ledger import (
    serialize_release_audit_ledger,
)
from app.connectors.repository.repository_release_audit_bundle import (
    RepositoryReleaseAuditBundleBuilder,
)
from app.connectors.repository.repository_release_audit_bundle_verification import (
    RepositoryReleaseAuditBundleVerification,
)
from app.connectors.repository.repository_release_audit_ledger import (
    GENESIS_HASH,
    RepositoryReleaseAuditLedger,
    RepositoryReleaseAuditLedgerBuilder,
    RepositoryReleaseAuditLedgerEntry,
    RepositoryReleaseAuditLedgerVerifier,
)
from app.connectors.repository.repository_release_audit_ledger_summary import (
    RepositoryReleaseAuditLedgerSummaryBuilder,
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
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    bundle = RepositoryReleaseAuditBundleBuilder().build(
        repository_path=str(repo),
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    return bundle.as_json()


def make_verification(
    bundle_id: str = "a" * 64,
    accepted: bool = True,
):
    return RepositoryReleaseAuditBundleVerification(
        bundle_id=bundle_id,
        package_id="b" * 64,
        report_id="c" * 64,
        certificate_id="d" * 64,
        attestation_id="e" * 64,
        repository_name="repo",
        schema_version="1.0",
        bundle_accepted=accepted,
        integrity_valid=True,
    )


def test_ledger_001_empty_latest_hash():
    ledger = RepositoryReleaseAuditLedger(
        schema_version="1.0",
        ledger_id="",
    )

    assert ledger.latest_entry_hash == GENESIS_HASH


def test_ledger_002_build_one_entry():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [make_verification()]
    )

    assert ledger.entry_count == 1


def test_ledger_003_sequence():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [
            make_verification("a" * 64),
            make_verification("b" * 64),
        ]
    )

    assert [entry.sequence for entry in ledger.entries] == [1, 2]


def test_ledger_004_chain_link():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [
            make_verification("a" * 64),
            make_verification("b" * 64),
        ]
    )

    assert (
        ledger.entries[1].previous_entry_hash
        == ledger.entries[0].entry_hash
    )


def test_ledger_005_counts():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [
            make_verification("a" * 64, True),
            make_verification("b" * 64, False),
        ]
    )

    assert ledger.accepted_entry_count == 1
    assert ledger.rejected_entry_count == 1


def test_ledger_006_repository_names():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [make_verification()]
    )

    assert ledger.repository_names == ["repo"]


def test_ledger_007_ledger_id():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [make_verification()]
    )

    assert len(ledger.ledger_id) == 64


def test_ledger_008_verification_valid():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [make_verification()]
    )

    verification = RepositoryReleaseAuditLedgerVerifier().verify(
        ledger
    )

    assert verification.valid is True


def test_ledger_009_tampered_entry():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [make_verification()]
    )

    entry = ledger.entries[0]

    tampered = RepositoryReleaseAuditLedger(
        schema_version=ledger.schema_version,
        ledger_id=ledger.ledger_id,
        entries=[
            RepositoryReleaseAuditLedgerEntry(
                sequence=entry.sequence,
                bundle_id="f" * 64,
                repository_name=entry.repository_name,
                accepted=entry.accepted,
                previous_entry_hash=entry.previous_entry_hash,
                entry_hash=entry.entry_hash,
            )
        ],
    )

    verification = RepositoryReleaseAuditLedgerVerifier().verify(
        tampered
    )

    assert verification.valid is False


def test_ledger_010_json():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [make_verification()]
    )

    assert '"ledger_id"' in ledger.as_json()


def test_ledger_011_markdown():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [make_verification()]
    )

    assert "# Repository Release Audit Ledger" in (
        ledger.as_markdown()
    )


def test_ledger_012_summary_accepted():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [make_verification()]
    )

    verification = RepositoryReleaseAuditLedgerVerifier().verify(
        ledger
    )

    summary = RepositoryReleaseAuditLedgerSummaryBuilder().build(
        ledger,
        verification,
    )

    assert summary.outcome == "ledger_accepted"


def test_ledger_013_summary_rejected():
    ledger = RepositoryReleaseAuditLedgerBuilder().from_verifications(
        [make_verification(accepted=False)]
    )

    verification = RepositoryReleaseAuditLedgerVerifier().verify(
        ledger
    )

    summary = RepositoryReleaseAuditLedgerSummaryBuilder().build(
        ledger,
        verification,
    )

    assert summary.outcome == "ledger_contains_rejections"


def test_ledger_014_real_bundle(tmp_path):
    ledger = RepositoryReleaseAuditLedgerBuilder().build(
        [make_bundle_json(tmp_path)]
    )

    assert ledger.entry_count == 1
    assert ledger.all_entries_accepted is True


def test_ledger_015_serialize(tmp_path):
    ledger = RepositoryReleaseAuditLedgerBuilder().build(
        [make_bundle_json(tmp_path)]
    )

    response = serialize_release_audit_ledger(ledger)

    assert response.ledger_valid is True
    assert response.entry_count == 1


def test_ledger_016_api(tmp_path):
    response = client.post(
        "/api/v1/repository-release-audit-ledger",
        json={
            "bundle_json_values": [
                make_bundle_json(tmp_path)
            ]
        },
    )

    assert response.status_code == 200
    assert response.json()["ledger_valid"] is True
    assert response.json()["entry_count"] == 1


def test_ledger_017_api_invalid_json():
    response = client.post(
        "/api/v1/repository-release-audit-ledger",
        json={
            "bundle_json_values": ["{invalid"]
        },
    )

    assert response.status_code == 400


def test_ledger_018_api_empty():
    response = client.post(
        "/api/v1/repository-release-audit-ledger",
        json={"bundle_json_values": []},
    )

    assert response.status_code == 422


def test_ledger_019_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-audit-ledger"
        in paths
    )


def test_ledger_020_route_supports_post():
    route = next(
        route
        for route in app.routes
        if (
            route.path
            == "/api/v1/repository-release-audit-ledger"
        )
    )

    assert "POST" in route.methods
