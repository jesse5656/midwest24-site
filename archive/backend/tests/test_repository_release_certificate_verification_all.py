import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_certificate_verification import (
    serialize_release_certificate_verification,
)
from app.connectors.repository.repository_release_certificate_verification import (
    RepositoryReleaseCertificateVerification,
    RepositoryReleaseCertificateVerificationIssue,
    RepositoryReleaseCertificateVerifier,
)
from app.connectors.repository.repository_release_certificate_verification_summary import (
    RepositoryReleaseCertificateVerificationSummaryBuilder,
)
from app.connectors.repository.repository_release_certification import (
    RepositoryReleaseCertificationBuilder,
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


def make_certificate_json(tmp_path: Path) -> str:
    repo = make_repo(tmp_path / "repo")

    baseline = RepositorySnapshotBaselineBuilder().build(
        repo
    )

    certification = RepositoryReleaseCertificationBuilder().build(
        repository_path=repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    return certification.as_json()


def make_verification(
    certified: bool = True,
    integrity_valid: bool = True,
    issues=None,
):
    return RepositoryReleaseCertificateVerification(
        certificate_id="a" * 64,
        repository_name="repo",
        schema_version="1.0",
        certified=certified,
        integrity_valid=integrity_valid,
        issues=issues or [],
    )


def test_verification_001_valid():
    assert make_verification().valid is True


def test_verification_002_accepted():
    assert make_verification().accepted is True


def test_verification_003_not_accepted_when_denied():
    assert make_verification(
        certified=False
    ).accepted is False


def test_verification_004_issue_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseCertificateVerificationIssue(
                "issue",
                "error",
                "Message.",
            )
        ]
    )
    assert verification.issue_count == 1


def test_verification_005_critical_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseCertificateVerificationIssue(
                "issue",
                "critical",
                "Message.",
            )
        ]
    )
    assert verification.critical_issue_count == 1


def test_verification_006_issue_codes():
    verification = make_verification(
        issues=[
            RepositoryReleaseCertificateVerificationIssue(
                "z",
                "warning",
                "Message.",
            ),
            RepositoryReleaseCertificateVerificationIssue(
                "a",
                "warning",
                "Message.",
            ),
        ]
    )
    assert verification.issue_codes == ["a", "z"]


def test_verification_007_status_accepted():
    assert make_verification().status == (
        "certificate_accepted"
    )


def test_verification_008_status_not_certified():
    assert make_verification(
        certified=False
    ).status == "certificate_valid_not_certified"


def test_verification_009_valid_certificate(tmp_path):
    verification = (
        RepositoryReleaseCertificateVerifier()
        .verify_json(make_certificate_json(tmp_path))
    )

    assert verification.accepted is True
    assert verification.integrity_valid is True


def test_verification_010_tampered_certificate(tmp_path):
    payload = json.loads(
        make_certificate_json(tmp_path)
    )
    payload["repository_name"] = "tampered"

    verification = (
        RepositoryReleaseCertificateVerifier()
        .verify_json(json.dumps(payload))
    )

    assert verification.valid is False
    assert "certificate_integrity_failure" in (
        verification.issue_codes
    )


def test_verification_011_bad_schema(tmp_path):
    payload = json.loads(
        make_certificate_json(tmp_path)
    )
    payload["schema_version"] = "999"
    payload["certificate_id"] = "a" * 64

    verification = (
        RepositoryReleaseCertificateVerifier()
        .verify_json(json.dumps(payload))
    )

    assert "unsupported_schema_version" in (
        verification.issue_codes
    )


def test_verification_012_expected_baseline(tmp_path):
    payload = json.loads(
        make_certificate_json(tmp_path)
    )

    verification = (
        RepositoryReleaseCertificateVerifier()
        .verify_json(
            json.dumps(payload),
            expected_baseline_fingerprint=(
                payload["baseline_fingerprint"]
            ),
        )
    )

    assert (
        "baseline_fingerprint_mismatch"
        not in verification.issue_codes
    )


def test_verification_013_baseline_mismatch(tmp_path):
    verification = (
        RepositoryReleaseCertificateVerifier()
        .verify_json(
            make_certificate_json(tmp_path),
            expected_baseline_fingerprint="different",
        )
    )

    assert "baseline_fingerprint_mismatch" in (
        verification.issue_codes
    )


def test_verification_014_invalid_json():
    try:
        RepositoryReleaseCertificateVerifier().verify_json(
            "{invalid"
        )
        assert False
    except ValueError:
        assert True


def test_verification_015_missing_fields():
    try:
        RepositoryReleaseCertificateVerifier().verify_json(
            "{}"
        )
        assert False
    except ValueError:
        assert True


def test_verification_016_summary_accepted():
    summary = (
        RepositoryReleaseCertificateVerificationSummaryBuilder()
        .build(make_verification())
    )
    assert summary.outcome == "certificate_accepted"


def test_verification_017_summary_critical():
    verification = make_verification(
        integrity_valid=False,
        issues=[
            RepositoryReleaseCertificateVerificationIssue(
                "integrity",
                "critical",
                "Failed.",
            )
        ],
    )

    summary = (
        RepositoryReleaseCertificateVerificationSummaryBuilder()
        .build(verification)
    )

    assert summary.outcome == (
        "certificate_rejected_critical"
    )


def test_verification_018_serialize():
    response = serialize_release_certificate_verification(
        make_verification()
    )

    assert response.accepted is True
    assert response.issue_count == 0


def test_verification_019_api_accepts(tmp_path):
    response = client.post(
        "/api/v1/repository-release-certificate-verification",
        json={
            "certificate_json": make_certificate_json(
                tmp_path
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_verification_020_api_rejects_tampered(tmp_path):
    payload = json.loads(
        make_certificate_json(tmp_path)
    )
    payload["repository_name"] = "tampered"

    response = client.post(
        "/api/v1/repository-release-certificate-verification",
        json={
            "certificate_json": json.dumps(payload)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_verification_021_api_invalid_json():
    response = client.post(
        "/api/v1/repository-release-certificate-verification",
        json={
            "certificate_json": "{invalid"
        },
    )

    assert response.status_code == 400


def test_verification_022_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-certificate-verification"
        in paths
    )


def test_verification_023_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path
        == "/api/v1/repository-release-certificate-verification"
    )

    assert "POST" in route.methods
