import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_audit_report import (
    serialize_repository_release_audit_report,
)
from app.connectors.repository.repository_release_audit_report import (
    RepositoryReleaseAuditFinding,
    RepositoryReleaseAuditReport,
    RepositoryReleaseAuditReportBuilder,
    verify_release_audit_report,
)
from app.connectors.repository.repository_release_audit_report_summary import (
    RepositoryReleaseAuditReportSummaryBuilder,
)
from app.connectors.repository.repository_release_evidence_package import (
    RepositoryReleaseEvidencePackageBuilder,
)
from app.connectors.repository.repository_release_evidence_package_verification import (
    RepositoryReleaseEvidencePackageVerification,
    RepositoryReleaseEvidencePackageVerificationIssue,
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


def make_package_json(tmp_path: Path) -> str:
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    package = RepositoryReleaseEvidencePackageBuilder().build(
        repository_path=repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    return package.as_json()


def make_report(
    passed: bool = True,
) -> RepositoryReleaseAuditReport:
    findings = [] if passed else [
        RepositoryReleaseAuditFinding(
            code="failure",
            severity="critical",
            message="Audit failed.",
        )
    ]

    provisional = RepositoryReleaseAuditReport(
        schema_version="1.0",
        report_id="",
        package_id="a" * 64,
        repository_name="repo",
        accepted=passed,
        integrity_valid=passed,
        status="audit_passed" if passed else "audit_failed",
        certificate_id="b" * 64,
        attestation_id="c" * 64,
        findings=findings,
    )

    import hashlib

    report_id = hashlib.sha256(
        provisional.canonical_json().encode("utf-8")
    ).hexdigest()

    return RepositoryReleaseAuditReport(
        schema_version=provisional.schema_version,
        report_id=report_id,
        package_id=provisional.package_id,
        repository_name=provisional.repository_name,
        accepted=provisional.accepted,
        integrity_valid=provisional.integrity_valid,
        status=provisional.status,
        certificate_id=provisional.certificate_id,
        attestation_id=provisional.attestation_id,
        findings=provisional.findings,
    )


def test_audit_001_passed():
    assert make_report(True).passed is True


def test_audit_002_failed():
    assert make_report(False).failed is True


def test_audit_003_exit_code_passed():
    assert make_report(True).exit_code == 0


def test_audit_004_exit_code_failed():
    assert make_report(False).exit_code == 1


def test_audit_005_finding_count():
    assert make_report(False).finding_count == 1


def test_audit_006_critical_count():
    assert make_report(False).critical_finding_count == 1


def test_audit_007_finding_codes():
    assert make_report(False).finding_codes == ["failure"]


def test_audit_008_report_valid():
    assert verify_release_audit_report(
        make_report(True)
    ) is True


def test_audit_009_markdown():
    markdown = make_report(True).as_markdown()

    assert "# Repository Release Audit Report" in markdown
    assert "**Passed:** Yes" in markdown


def test_audit_010_json():
    payload = json.loads(make_report(True).as_json())

    assert payload["passed"] is True
    assert len(payload["report_id"]) == 64


def test_audit_011_from_verification_passed():
    verification = RepositoryReleaseEvidencePackageVerification(
        package_id="a" * 64,
        repository_name="repo",
        schema_version="1.0",
        certificate_id="b" * 64,
        attestation_id="c" * 64,
        integrity_valid=True,
        package_accepted=True,
    )

    report = RepositoryReleaseAuditReportBuilder().from_verification(
        verification
    )

    assert report.passed is True
    assert len(report.report_id) == 64


def test_audit_012_from_verification_failed():
    verification = RepositoryReleaseEvidencePackageVerification(
        package_id="a" * 64,
        repository_name="repo",
        schema_version="1.0",
        certificate_id="b" * 64,
        attestation_id="c" * 64,
        integrity_valid=False,
        package_accepted=False,
        issues=[
            RepositoryReleaseEvidencePackageVerificationIssue(
                code="integrity",
                severity="critical",
                message="Failed.",
            )
        ],
    )

    report = RepositoryReleaseAuditReportBuilder().from_verification(
        verification
    )

    assert report.failed is True
    assert report.critical_finding_count == 1


def test_audit_013_real_package(tmp_path):
    report = RepositoryReleaseAuditReportBuilder().build(
        make_package_json(tmp_path)
    )

    assert report.passed is True
    assert verify_release_audit_report(report) is True


def test_audit_014_tampered_package(tmp_path):
    payload = json.loads(make_package_json(tmp_path))
    payload["repository_name"] = "tampered"

    report = RepositoryReleaseAuditReportBuilder().build(
        json.dumps(payload)
    )

    assert report.failed is True
    assert "package_integrity_failure" in report.finding_codes


def test_audit_015_summary_passed():
    summary = RepositoryReleaseAuditReportSummaryBuilder().build(
        make_report(True)
    )

    assert summary.outcome == "release_audit_passed"


def test_audit_016_summary_critical():
    summary = RepositoryReleaseAuditReportSummaryBuilder().build(
        make_report(False)
    )

    assert summary.outcome == "release_audit_failed_critical"


def test_audit_017_serialize():
    response = serialize_repository_release_audit_report(
        make_report(True)
    )

    assert response.passed is True
    assert response.report_valid is True


def test_audit_018_api_passed(tmp_path):
    response = client.post(
        "/api/v1/repository-release-audit-report",
        json={
            "package_json": make_package_json(tmp_path)
        },
    )

    assert response.status_code == 200
    assert response.json()["passed"] is True
    assert response.json()["report_valid"] is True


def test_audit_019_api_tampered(tmp_path):
    payload = json.loads(make_package_json(tmp_path))
    payload["repository_name"] = "tampered"

    response = client.post(
        "/api/v1/repository-release-audit-report",
        json={
            "package_json": json.dumps(payload)
        },
    )

    assert response.status_code == 200
    assert response.json()["failed"] is True


def test_audit_020_api_invalid_json():
    response = client.post(
        "/api/v1/repository-release-audit-report",
        json={"package_json": "{invalid"},
    )

    assert response.status_code == 400


def test_audit_021_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-audit-report"
        in paths
    )


def test_audit_022_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path
        == "/api/v1/repository-release-audit-report"
    )

    assert "POST" in route.methods
