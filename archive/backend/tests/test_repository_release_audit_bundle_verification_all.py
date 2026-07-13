import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_audit_bundle_verification import (
    serialize_release_audit_bundle_verification,
)
from app.connectors.repository.repository_release_audit_bundle import (
    RepositoryReleaseAuditBundleBuilder,
)
from app.connectors.repository.repository_release_audit_bundle_verification import (
    RepositoryReleaseAuditBundleVerification,
    RepositoryReleaseAuditBundleVerificationIssue,
    RepositoryReleaseAuditBundleVerifier,
)
from app.connectors.repository.repository_release_audit_bundle_verification_summary import (
    RepositoryReleaseAuditBundleVerificationSummaryBuilder,
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
    accepted: bool = True,
    integrity_valid: bool = True,
    issues=None,
):
    return RepositoryReleaseAuditBundleVerification(
        bundle_id="a" * 64,
        package_id="b" * 64,
        report_id="c" * 64,
        certificate_id="d" * 64,
        attestation_id="e" * 64,
        repository_name="repo",
        schema_version="1.0",
        bundle_accepted=accepted,
        integrity_valid=integrity_valid,
        issues=issues or [],
    )


def test_bundle_verification_001_valid():
    assert make_verification().valid is True


def test_bundle_verification_002_accepted():
    assert make_verification().accepted is True


def test_bundle_verification_003_rejected():
    assert make_verification(
        accepted=False
    ).rejected is True


def test_bundle_verification_004_issue_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditBundleVerificationIssue(
                "issue",
                "error",
                "Message.",
            )
        ]
    )

    assert verification.issue_count == 1


def test_bundle_verification_005_critical_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditBundleVerificationIssue(
                "issue",
                "critical",
                "Message.",
            )
        ]
    )

    assert verification.critical_issue_count == 1


def test_bundle_verification_006_issue_codes():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditBundleVerificationIssue(
                "z",
                "warning",
                "Message.",
            ),
            RepositoryReleaseAuditBundleVerificationIssue(
                "a",
                "warning",
                "Message.",
            ),
        ]
    )

    assert verification.issue_codes == ["a", "z"]


def test_bundle_verification_007_status():
    assert make_verification().status == (
        "release_audit_bundle_accepted"
    )


def test_bundle_verification_008_real_bundle(tmp_path):
    verification = (
        RepositoryReleaseAuditBundleVerifier()
        .verify_json(make_bundle_json(tmp_path))
    )

    assert verification.accepted is True
    assert verification.integrity_valid is True


def test_bundle_verification_009_tampered(tmp_path):
    payload = json.loads(make_bundle_json(tmp_path))
    payload["repository_name"] = "tampered"

    verification = (
        RepositoryReleaseAuditBundleVerifier()
        .verify_json(json.dumps(payload))
    )

    assert verification.valid is False
    assert "bundle_integrity_failure" in (
        verification.issue_codes
    )


def test_bundle_verification_010_bad_schema(tmp_path):
    payload = json.loads(make_bundle_json(tmp_path))
    payload["schema_version"] = "999"
    payload["bundle_id"] = "a" * 64

    verification = (
        RepositoryReleaseAuditBundleVerifier()
        .verify_json(json.dumps(payload))
    )

    assert "unsupported_schema_version" in (
        verification.issue_codes
    )


def test_bundle_verification_011_package_mismatch(
    tmp_path,
):
    verification = (
        RepositoryReleaseAuditBundleVerifier()
        .verify_json(
            make_bundle_json(tmp_path),
            expected_package_id="different",
        )
    )

    assert "package_id_mismatch" in (
        verification.issue_codes
    )


def test_bundle_verification_012_report_mismatch(
    tmp_path,
):
    verification = (
        RepositoryReleaseAuditBundleVerifier()
        .verify_json(
            make_bundle_json(tmp_path),
            expected_report_id="different",
        )
    )

    assert "report_id_mismatch" in (
        verification.issue_codes
    )


def test_bundle_verification_013_invalid_json():
    try:
        RepositoryReleaseAuditBundleVerifier().verify_json(
            "{invalid"
        )
        assert False
    except ValueError:
        assert True


def test_bundle_verification_014_missing_fields():
    try:
        RepositoryReleaseAuditBundleVerifier().verify_json(
            "{}"
        )
        assert False
    except ValueError:
        assert True


def test_bundle_verification_015_summary_accepted():
    summary = (
        RepositoryReleaseAuditBundleVerificationSummaryBuilder()
        .build(make_verification())
    )

    assert summary.outcome == (
        "release_audit_bundle_accepted"
    )


def test_bundle_verification_016_summary_critical():
    verification = make_verification(
        integrity_valid=False,
        issues=[
            RepositoryReleaseAuditBundleVerificationIssue(
                "integrity",
                "critical",
                "Failed.",
            )
        ],
    )

    summary = (
        RepositoryReleaseAuditBundleVerificationSummaryBuilder()
        .build(verification)
    )

    assert summary.outcome == (
        "release_audit_bundle_rejected_critical"
    )


def test_bundle_verification_017_serialize():
    response = serialize_release_audit_bundle_verification(
        make_verification()
    )

    assert response.accepted is True
    assert response.issue_count == 0


def test_bundle_verification_018_api_accepts(tmp_path):
    response = client.post(
        "/api/v1/repository-release-audit-bundle-verification",
        json={
            "bundle_json": make_bundle_json(tmp_path)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_bundle_verification_019_api_tampered(tmp_path):
    payload = json.loads(make_bundle_json(tmp_path))
    payload["repository_name"] = "tampered"

    response = client.post(
        "/api/v1/repository-release-audit-bundle-verification",
        json={
            "bundle_json": json.dumps(payload)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_bundle_verification_020_api_invalid_json():
    response = client.post(
        "/api/v1/repository-release-audit-bundle-verification",
        json={"bundle_json": "{invalid"},
    )

    assert response.status_code == 400


def test_bundle_verification_021_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-audit-bundle-verification"
        in paths
    )


def test_bundle_verification_022_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path
        == "/api/v1/repository-release-audit-bundle-verification"
    )

    assert "POST" in route.methods
