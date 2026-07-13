import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_evidence_package_verification import (
    serialize_release_evidence_package_verification,
)
from app.connectors.repository.repository_release_evidence_package import (
    RepositoryReleaseEvidencePackageBuilder,
)
from app.connectors.repository.repository_release_evidence_package_verification import (
    RepositoryReleaseEvidencePackageVerification,
    RepositoryReleaseEvidencePackageVerificationIssue,
    RepositoryReleaseEvidencePackageVerifier,
)
from app.connectors.repository.repository_release_evidence_package_verification_summary import (
    RepositoryReleaseEvidencePackageVerificationSummaryBuilder,
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


def make_verification(
    accepted=True,
    integrity_valid=True,
    issues=None,
):
    return RepositoryReleaseEvidencePackageVerification(
        package_id="a" * 64,
        repository_name="repo",
        schema_version="1.0",
        certificate_id="b" * 64,
        attestation_id="c" * 64,
        integrity_valid=integrity_valid,
        package_accepted=accepted,
        issues=issues or [],
    )


def test_package_verification_001_valid():
    assert make_verification().valid is True


def test_package_verification_002_accepted():
    assert make_verification().accepted is True


def test_package_verification_003_rejected():
    assert make_verification(
        accepted=False
    ).rejected is True


def test_package_verification_004_issue_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseEvidencePackageVerificationIssue(
                "issue",
                "error",
                "Message.",
            )
        ]
    )
    assert verification.issue_count == 1


def test_package_verification_005_critical_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseEvidencePackageVerificationIssue(
                "issue",
                "critical",
                "Message.",
            )
        ]
    )
    assert verification.critical_issue_count == 1


def test_package_verification_006_status():
    assert make_verification().status == (
        "release_package_accepted"
    )


def test_package_verification_007_real_package(tmp_path):
    verification = (
        RepositoryReleaseEvidencePackageVerifier()
        .verify_json(make_package_json(tmp_path))
    )

    assert verification.accepted is True
    assert verification.integrity_valid is True


def test_package_verification_008_tampered(tmp_path):
    payload = json.loads(
        make_package_json(tmp_path)
    )
    payload["repository_name"] = "tampered"

    verification = (
        RepositoryReleaseEvidencePackageVerifier()
        .verify_json(json.dumps(payload))
    )

    assert verification.valid is False
    assert "package_integrity_failure" in (
        verification.issue_codes
    )


def test_package_verification_009_bad_schema(tmp_path):
    payload = json.loads(
        make_package_json(tmp_path)
    )
    payload["schema_version"] = "999"
    payload["package_id"] = "a" * 64

    verification = (
        RepositoryReleaseEvidencePackageVerifier()
        .verify_json(json.dumps(payload))
    )

    assert "unsupported_schema_version" in (
        verification.issue_codes
    )


def test_package_verification_010_certificate_mismatch(
    tmp_path,
):
    verification = (
        RepositoryReleaseEvidencePackageVerifier()
        .verify_json(
            make_package_json(tmp_path),
            expected_certificate_id="different",
        )
    )

    assert "certificate_id_mismatch" in (
        verification.issue_codes
    )


def test_package_verification_011_attestation_mismatch(
    tmp_path,
):
    verification = (
        RepositoryReleaseEvidencePackageVerifier()
        .verify_json(
            make_package_json(tmp_path),
            expected_attestation_id="different",
        )
    )

    assert "attestation_id_mismatch" in (
        verification.issue_codes
    )


def test_package_verification_012_invalid_json():
    try:
        RepositoryReleaseEvidencePackageVerifier().verify_json(
            "{invalid"
        )
        assert False
    except ValueError:
        assert True


def test_package_verification_013_missing_fields():
    try:
        RepositoryReleaseEvidencePackageVerifier().verify_json(
            "{}"
        )
        assert False
    except ValueError:
        assert True


def test_package_verification_014_summary_accepted():
    summary = (
        RepositoryReleaseEvidencePackageVerificationSummaryBuilder()
        .build(make_verification())
    )

    assert summary.outcome == "release_package_accepted"


def test_package_verification_015_summary_critical():
    verification = make_verification(
        integrity_valid=False,
        issues=[
            RepositoryReleaseEvidencePackageVerificationIssue(
                "integrity",
                "critical",
                "Failed.",
            )
        ],
    )

    summary = (
        RepositoryReleaseEvidencePackageVerificationSummaryBuilder()
        .build(verification)
    )

    assert summary.outcome == (
        "release_package_rejected_critical"
    )


def test_package_verification_016_serialize():
    response = serialize_release_evidence_package_verification(
        make_verification()
    )

    assert response.accepted is True
    assert response.issue_count == 0


def test_package_verification_017_api_accepts(tmp_path):
    response = client.post(
        "/api/v1/repository-release-evidence-package-verification",
        json={
            "package_json": make_package_json(tmp_path)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_package_verification_018_api_tampered(tmp_path):
    payload = json.loads(
        make_package_json(tmp_path)
    )
    payload["repository_name"] = "tampered"

    response = client.post(
        "/api/v1/repository-release-evidence-package-verification",
        json={
            "package_json": json.dumps(payload)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_package_verification_019_api_invalid_json():
    response = client.post(
        "/api/v1/repository-release-evidence-package-verification",
        json={"package_json": "{invalid"},
    )

    assert response.status_code == 400


def test_package_verification_020_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-evidence-package-verification"
        in paths
    )


def test_package_verification_021_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path
        == "/api/v1/repository-release-evidence-package-verification"
    )

    assert "POST" in route.methods
