import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_attestation_verification import (
    serialize_release_attestation_verification,
)
from app.connectors.repository.repository_release_attestation import (
    RepositoryReleaseAttestationBuilder,
)
from app.connectors.repository.repository_release_attestation_verification import (
    RepositoryReleaseAttestationVerification,
    RepositoryReleaseAttestationVerificationIssue,
    RepositoryReleaseAttestationVerifier,
)
from app.connectors.repository.repository_release_attestation_verification_summary import (
    RepositoryReleaseAttestationVerificationSummaryBuilder,
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


def make_attestation_json(tmp_path: Path) -> str:
    repo = make_repo(tmp_path / "repo")

    baseline = RepositorySnapshotBaselineBuilder().build(
        repo
    )

    attestation = RepositoryReleaseAttestationBuilder().build(
        repository_path=repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    return attestation.as_json()


def make_verification(
    accepted: bool = True,
    integrity_valid: bool = True,
    issues=None,
):
    return RepositoryReleaseAttestationVerification(
        attestation_id="a" * 64,
        certificate_id="b" * 64,
        repository_name="repo",
        schema_version="1.0",
        certified=accepted,
        certificate_valid=accepted,
        integrity_valid=integrity_valid,
        issues=issues or [],
    )


def test_attestation_verification_001_valid():
    assert make_verification().valid is True


def test_attestation_verification_002_accepted():
    assert make_verification().accepted is True


def test_attestation_verification_003_rejected():
    assert make_verification(
        accepted=False
    ).rejected is True


def test_attestation_verification_004_issue_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseAttestationVerificationIssue(
                "issue",
                "error",
                "Message.",
            )
        ]
    )
    assert verification.issue_count == 1


def test_attestation_verification_005_critical_count():
    verification = make_verification(
        issues=[
            RepositoryReleaseAttestationVerificationIssue(
                "issue",
                "critical",
                "Message.",
            )
        ]
    )
    assert verification.critical_issue_count == 1


def test_attestation_verification_006_issue_codes():
    verification = make_verification(
        issues=[
            RepositoryReleaseAttestationVerificationIssue(
                "z",
                "warning",
                "Message.",
            ),
            RepositoryReleaseAttestationVerificationIssue(
                "a",
                "warning",
                "Message.",
            ),
        ]
    )
    assert verification.issue_codes == ["a", "z"]


def test_attestation_verification_007_status_accepted():
    assert make_verification().status == (
        "attestation_accepted"
    )


def test_attestation_verification_008_valid_attestation(tmp_path):
    verification = (
        RepositoryReleaseAttestationVerifier()
        .verify_json(make_attestation_json(tmp_path))
    )

    assert verification.accepted is True
    assert verification.integrity_valid is True


def test_attestation_verification_009_tampered(tmp_path):
    payload = json.loads(
        make_attestation_json(tmp_path)
    )
    payload["repository_name"] = "tampered"

    verification = (
        RepositoryReleaseAttestationVerifier()
        .verify_json(json.dumps(payload))
    )

    assert verification.valid is False
    assert "attestation_integrity_failure" in (
        verification.issue_codes
    )


def test_attestation_verification_010_bad_schema(tmp_path):
    payload = json.loads(
        make_attestation_json(tmp_path)
    )
    payload["schema_version"] = "999"
    payload["attestation_id"] = "a" * 64

    verification = (
        RepositoryReleaseAttestationVerifier()
        .verify_json(json.dumps(payload))
    )

    assert "unsupported_schema_version" in (
        verification.issue_codes
    )


def test_attestation_verification_011_certificate_mismatch(
    tmp_path,
):
    verification = (
        RepositoryReleaseAttestationVerifier()
        .verify_json(
            make_attestation_json(tmp_path),
            expected_certificate_id="different",
        )
    )

    assert "certificate_id_mismatch" in (
        verification.issue_codes
    )


def test_attestation_verification_012_invalid_json():
    try:
        RepositoryReleaseAttestationVerifier().verify_json(
            "{invalid"
        )
        assert False
    except ValueError:
        assert True


def test_attestation_verification_013_missing_fields():
    try:
        RepositoryReleaseAttestationVerifier().verify_json(
            "{}"
        )
        assert False
    except ValueError:
        assert True


def test_attestation_verification_014_summary_accepted():
    summary = (
        RepositoryReleaseAttestationVerificationSummaryBuilder()
        .build(make_verification())
    )

    assert summary.outcome == "attestation_accepted"


def test_attestation_verification_015_summary_critical():
    verification = make_verification(
        integrity_valid=False,
        issues=[
            RepositoryReleaseAttestationVerificationIssue(
                "integrity",
                "critical",
                "Failed.",
            )
        ],
    )

    summary = (
        RepositoryReleaseAttestationVerificationSummaryBuilder()
        .build(verification)
    )

    assert summary.outcome == (
        "attestation_rejected_critical"
    )


def test_attestation_verification_016_serialize():
    response = serialize_release_attestation_verification(
        make_verification()
    )

    assert response.accepted is True
    assert response.issue_count == 0


def test_attestation_verification_017_api_accepts(tmp_path):
    response = client.post(
        "/api/v1/repository-release-attestation-verification",
        json={
            "attestation_json": make_attestation_json(
                tmp_path
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_attestation_verification_018_api_rejects_tampered(
    tmp_path,
):
    payload = json.loads(
        make_attestation_json(tmp_path)
    )
    payload["repository_name"] = "tampered"

    response = client.post(
        "/api/v1/repository-release-attestation-verification",
        json={
            "attestation_json": json.dumps(payload)
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is False


def test_attestation_verification_019_api_invalid_json():
    response = client.post(
        "/api/v1/repository-release-attestation-verification",
        json={
            "attestation_json": "{invalid"
        },
    )

    assert response.status_code == 400


def test_attestation_verification_020_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-attestation-verification"
        in paths
    )


def test_attestation_verification_021_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path
        == "/api/v1/repository-release-attestation-verification"
    )

    assert "POST" in route.methods
