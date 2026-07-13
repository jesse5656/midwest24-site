from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_attestation import (
    serialize_repository_release_attestation,
)
from app.connectors.repository.repository_release_attestation import (
    ATTESTATION_SCHEMA_VERSION,
    RepositoryReleaseAttestation,
    RepositoryReleaseAttestationBuilder,
    RepositoryReleaseAttestationEvidence,
    verify_release_attestation,
)
from app.connectors.repository.repository_release_attestation_summary import (
    RepositoryReleaseAttestationSummaryBuilder,
)
from app.connectors.repository.repository_release_certificate_verification import (
    RepositoryReleaseCertificateVerification,
)
from app.connectors.repository.repository_release_certification import (
    RepositoryReleaseCertification,
    RepositoryReleaseCertificationEvidence,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaselineBuilder,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)
from app.main import app

client = TestClient(app)


def make_repo(
    root: Path,
    changed: bool = False,
) -> Path:
    root.mkdir()

    root.joinpath("requirements.txt").write_text(
        (
            "fastapi\npytest\nsqlalchemy\n"
            if changed
            else "fastapi\npytest\n"
        ),
        encoding="utf-8",
    )

    root.joinpath("app.py").write_text(
        (
            "import os\n"
            "import json\n"
            "class Worker:\n"
            "    def run(self):\n"
            "        return json.dumps({})\n"
            if changed
            else
            "import os\n"
            "class Worker:\n"
            "    def run(self):\n"
            "        return os.getcwd()\n"
        ),
        encoding="utf-8",
    )

    if changed:
        root.joinpath("extra.py").write_text(
            "def extra_function():\n"
            "    return True\n",
            encoding="utf-8",
        )

    return root


def make_attestation(
    accepted: bool = True,
) -> RepositoryReleaseAttestation:
    evidence = [
        RepositoryReleaseAttestationEvidence(
            name="snapshot_gate",
            passed=accepted,
            severity="critical",
            message="Passed." if accepted else "Failed.",
        )
    ]

    provisional = RepositoryReleaseAttestation(
        schema_version=ATTESTATION_SCHEMA_VERSION,
        repository_path="/repo",
        repository_name="repo",
        attestation_id="",
        certificate_id="a" * 64,
        certificate_valid=accepted,
        certified=accepted,
        baseline_fingerprint="b" * 64,
        candidate_fingerprint="b" * 64,
        evidence=evidence,
        issues=[] if accepted else ["certificate_not_certified"],
    )

    import hashlib

    attestation_id = hashlib.sha256(
        provisional.canonical_json().encode("utf-8")
    ).hexdigest()

    return RepositoryReleaseAttestation(
        schema_version=provisional.schema_version,
        repository_path=provisional.repository_path,
        repository_name=provisional.repository_name,
        attestation_id=attestation_id,
        certificate_id=provisional.certificate_id,
        certificate_valid=provisional.certificate_valid,
        certified=provisional.certified,
        baseline_fingerprint=provisional.baseline_fingerprint,
        candidate_fingerprint=provisional.candidate_fingerprint,
        evidence=provisional.evidence,
        issues=provisional.issues,
    )


def test_attestation_001_accepted():
    assert make_attestation(True).accepted is True


def test_attestation_002_rejected():
    assert make_attestation(False).rejected is True


def test_attestation_003_evidence_count():
    assert make_attestation(True).evidence_count == 1


def test_attestation_004_passed_evidence_count():
    assert make_attestation(True).passed_evidence_count == 1


def test_attestation_005_failed_evidence_count():
    assert make_attestation(False).failed_evidence_count == 1


def test_attestation_006_issue_count():
    assert make_attestation(False).issue_count == 1


def test_attestation_007_status():
    assert make_attestation(True).status == (
        "attestation_accepted"
    )


def test_attestation_008_attestation_valid():
    assert verify_release_attestation(
        make_attestation(True)
    ) is True


def test_attestation_009_summary_accepted():
    summary = RepositoryReleaseAttestationSummaryBuilder().build(
        make_attestation(True)
    )
    assert summary.outcome == "attestation_accepted"


def test_attestation_010_summary_rejected():
    summary = RepositoryReleaseAttestationSummaryBuilder().build(
        make_attestation(False)
    )
    assert summary.outcome == (
        "attestation_rejected_invalid_certificate"
    )


def test_attestation_011_serialize():
    response = serialize_repository_release_attestation(
        make_attestation(True)
    )
    assert response.accepted is True
    assert response.attestation_valid is True


def test_attestation_012_builder_from_certification():
    certification = RepositoryReleaseCertification(
        schema_version="1.0",
        repository_path="/repo",
        repository_name="repo",
        release_ready=True,
        status="certified",
        certificate_id="a" * 64,
        baseline_fingerprint="b" * 64,
        candidate_fingerprint="b" * 64,
        evidence=[
            RepositoryReleaseCertificationEvidence(
                name="snapshot_gate",
                passed=True,
                severity="critical",
                message="Passed.",
            )
        ],
    )

    verification = RepositoryReleaseCertificateVerification(
        certificate_id="a" * 64,
        repository_name="repo",
        schema_version="1.0",
        certified=True,
        integrity_valid=True,
    )

    attestation = (
        RepositoryReleaseAttestationBuilder()
        .from_certification(
            certification=certification,
            verification=verification,
        )
    )

    assert attestation.accepted is True
    assert len(attestation.attestation_id) == 64


def test_attestation_013_real_repository_accepted(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    attestation = RepositoryReleaseAttestationBuilder().build(
        repository_path=repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    assert attestation.accepted is True


def test_attestation_014_changed_repository_rejected(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    attestation = RepositoryReleaseAttestationBuilder().build(
        repository_path=candidate_repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    assert attestation.rejected is True


def test_attestation_015_api_accepted(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    response = client.post(
        "/api/v1/repository-release-attestation",
        json={
            "repository_path": str(repo),
            "baseline_json": baseline.to_json(),
            "policy": {
                "require_fingerprint_match": True
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["attestation_valid"] is True


def test_attestation_016_api_rejected(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    response = client.post(
        "/api/v1/repository-release-attestation",
        json={
            "repository_path": str(candidate_repo),
            "baseline_json": baseline.to_json(),
            "policy": {
                "require_fingerprint_match": True
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["rejected"] is True


def test_attestation_017_api_invalid_baseline(tmp_path):
    repo = make_repo(tmp_path / "repo")

    response = client.post(
        "/api/v1/repository-release-attestation",
        json={
            "repository_path": str(repo),
            "baseline_json": "{invalid",
        },
    )

    assert response.status_code == 400


def test_attestation_018_api_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-release-attestation",
        json={
            "repository_path": str(tmp_path / "missing"),
            "baseline_json": "{}",
        },
    )

    assert response.status_code == 400


def test_attestation_019_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-attestation"
        in paths
    )


def test_attestation_020_route_supports_post():
    route = next(
        route
        for route in app.routes
        if (
            route.path
            == "/api/v1/repository-release-attestation"
        )
    )

    assert "POST" in route.methods
