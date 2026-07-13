import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_audit_report_verification import (
    serialize_release_audit_report_verification,
)
from app.connectors.repository.repository_release_audit_report import (
    RepositoryReleaseAuditReportBuilder,
)
from app.connectors.repository.repository_release_audit_report_verification import (
    RepositoryReleaseAuditReportVerification,
    RepositoryReleaseAuditReportVerificationIssue,
    RepositoryReleaseAuditReportVerifier,
)
from app.connectors.repository.repository_release_audit_report_verification_summary import (
    RepositoryReleaseAuditReportVerificationSummaryBuilder,
)
from app.connectors.repository.repository_release_evidence_package import (
    RepositoryReleaseEvidencePackageBuilder,
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


def make_report_json(tmp_path: Path) -> str:
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    package = RepositoryReleaseEvidencePackageBuilder().build(
        repository_path=repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    report = RepositoryReleaseAuditReportBuilder().build(
        package.as_json()
    )

    return report.as_json()


def make_verification(
    accepted: bool = True,
    integrity_valid: bool = True,
    issues=None,
):
    return RepositoryReleaseAuditReportVerification(
        report_id="a" * 64,
        package_id="b" * 64,
        certificate_id="c" * 64,
        attestation_id="d" * 64,
        repository_name="repo",
        schema_version="1.0",
        report_passed=accepted,
        integrity_valid=integrity_valid,
        issues=issues or [],
    )


def test_audit_verification_001_valid():
    assert make_verification().valid is True


def test_audit_verification_002_accepted():
    assert make_verification().accepted is True


def test_audit_verification_003_rejected():
    assert make_verification(
        accepted=False
    ).rejected is True


def test_audit_verification_004_issue_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditReportVerificationIssue(
                "issue",
                "error",
                "Message.",
            )
        ]
    )
    assert verification.issue_count == 1


def test_audit_verification_005_critical_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditReportVerificationIssue(
                "issue",
                "critical",
                "Message.",
            )
        ]
    )
    assert verification.critical_issue_count == 1


def test_audit_verification_006_issue_codes():
    verification = make_verification(
        issues=[
            RepositoryReleaseAuditReportVerificationIssue(
                "z",
                "warning",
                "Message.",
            ),
            RepositoryReleaseAuditReportVerificationIssue(
                "a",
                "warning",
                "Message.",
            ),
        ]
    )
    assert verification.issue_codes == ["a", "z"]


def test_audit_verification_007_status():
    assert make_verification().status == (
        "release_audit_report_accepted"
    )


def test_audit_verification_008_real_report(tmp_path):
    verification = (
        RepositoryReleaseAuditReportVerifier()
        .verify_json(make_report_json(tmp_path))
    )

    assert verification.accepted is True
    assert verification.integrity_valid is True


def test_audit_verification_009_tampered(tmp_path):
    payload = json.loads(make_report_json(tmp_path))
    payload["repository_name"] = "tampered"

    verification = (
        RepositoryReleaseAuditReportVerifier()
        .verify_json(json.dumps(payload))
    )

    assert verification.valid is False
    assert "report_integrity_failure" in (
        verification.issue_codes
    )


def test_audit_verification_010_bad_schema(tmp_path):
    payload = json.loads(make_report_json(tmp_path))
    payload["schema_version"] = "999"
    payload["report_id"] = "a" * 64

    verification = (
        RepositoryReleaseAuditReportVerifier()
        .verify_json(json.dumps(payload))
    )

    assert "unsupported_schema_version" in (
        verification.issue_codes
    )


def test_audit_verification_011_package_mismatch(
    tmp_path,
):
    verification = (
        RepositoryReleaseAuditReportVerifier()
        .verify_json(
            make_report_json(tmp_path),
            expected_package_id="different",
        )
    )

    assert "package_id_mismatch" in (
        verification.issue_codes
    )


def test_audit_verification_012_certificate_mismatch(
    tmp_path,
):
    verification = (
        RepositoryReleaseAuditReportVerifier()
        .verify_json(
            make_report_json(tmp_path),
            expected_certificate_id="different",
        )
    )

    assert "certificate_id_mismatch" in (
        verification.issue_codes
    )


def test_audit_verification_013_invalid_json():
    try:
        RepositoryReleaseAuditReportVerifier().verify_json(
            "{invalid"
        )
        assert False
    except ValueError:
        assert True


def test_audit_verification_014_missing_fields():
    try:
        RepositoryReleaseAuditReportVerifier().verify_json(
            "{}"
        )
        assert False
    except ValueError:
        assert True


def test_audit_verification_015_summary_accepted():
    summary = (
        RepositoryReleaseAuditReportVerificationSummaryBuilder()
        .build(make_verification())
    )

    assert summary.outcome == (
        "release_audit_report_accepted"
    )


def test_audit_verification_016_summary_critical():
    verification = make_verification(
        integrity_valid=False,
        issues=[
            RepositoryReleaseAuditReportVerificationIssue(
                "integrity",
                "critical",
                "Failed.",
            )
        ],
    )

    summary = (
        RepositoryReleaseAuditReportVerificationSummaryBuilder()
        .build(verification)
    )

    assert summary.outcome == (
        "release_audit_report_rejected_critical"
    )


def test_audit_verification_017_serialize():
    response = serialize_release_audit_report_verification(
        make_verification()
    )

    assert response.accepted is True
    assert response.issue_count == 0


def test_audit_verification_018_api_accepts(tmp_path):
    response = client.post(
        "/api/v1/repository-release-audit-report-verification",
        json={
            "report_json": make_report_json(tmp_path)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_audit_verification_019_api_tampered(tmp_path):
    payload = json.loads(make_report_json(tmp_path))
    payload["repository_name"] = "tampered"

    response = client.post(
        "/api/v1/repository-release-audit-report-verification",
        json={
            "report_json": json.dumps(payload)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_audit_verification_020_api_invalid_json():
    response = client.post(
        "/api/v1/repository-release-audit-report-verification",
        json={"report_json": "{invalid"},
    )

    assert response.status_code == 400


def test_audit_verification_021_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-audit-report-verification"
        in paths
    )


def test_audit_verification_022_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path
        == "/api/v1/repository-release-audit-report-verification"
    )

    assert "POST" in route.methods
