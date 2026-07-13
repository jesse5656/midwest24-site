from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_certification import (
    serialize_repository_release_certification,
)
from app.connectors.repository.repository_intelligence_dashboard import (
    RepositoryIntelligenceDashboard,
)
from app.connectors.repository.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshot,
)
from app.connectors.repository.repository_release_certification import (
    CERTIFICATION_SCHEMA_VERSION,
    RepositoryReleaseCertification,
    RepositoryReleaseCertificationBuilder,
    RepositoryReleaseCertificationEvidence,
    verify_release_certificate,
)
from app.connectors.repository.repository_release_certification_summary import (
    RepositoryReleaseCertificationSummaryBuilder,
)
from app.connectors.repository.repository_release_readiness import (
    RepositoryReleaseReadiness,
    RepositoryReleaseReadinessCheck,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaselineBuilder,
    RepositorySnapshotBaselineVerification,
)
from app.connectors.repository.repository_snapshot_gate import (
    RepositorySnapshotGateResult,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
    RepositorySnapshotPolicyEvaluation,
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


def make_readiness(
    ready: bool = True,
) -> tuple[RepositoryReleaseReadiness, object]:
    snapshot = RepositoryIntelligenceSnapshot(
        repository_path="/repo",
        repository_name="repo",
        fingerprint="same",
    )

    baseline = RepositorySnapshotBaselineBuilder().from_snapshot(
        snapshot
    )

    verification = RepositorySnapshotBaselineVerification(
        baseline=baseline,
        candidate=snapshot,
        fingerprint_matches=ready,
        metric_differences=[] if ready else ["changed"],
    )

    policy_evaluation = RepositorySnapshotPolicyEvaluation(
        repository_path="/repo",
        baseline_fingerprint="same",
        candidate_fingerprint="same",
        policy=RepositorySnapshotPolicy(),
        violations=[],
    )

    gate = RepositorySnapshotGateResult(
        repository_path="/repo",
        baseline_verification=verification,
        policy_evaluation=policy_evaluation,
        reasons=[],
    )

    checks = [
        RepositoryReleaseReadinessCheck(
            name="snapshot_gate",
            passed=ready,
            severity="critical",
            message="Passed." if ready else "Failed.",
        ),
        RepositoryReleaseReadinessCheck(
            name="intelligence_dashboard",
            passed=True,
            severity="critical",
            message="Passed.",
        ),
    ]

    readiness = RepositoryReleaseReadiness(
        repository_path="/repo",
        repository_name="repo",
        gate=gate,
        dashboard=RepositoryIntelligenceDashboard(
            repository_path="/repo",
            repository_name="repo",
        ),
        checks=checks,
    )

    return readiness, baseline


def make_certification(
    certified: bool = True,
) -> RepositoryReleaseCertification:
    evidence = [
        RepositoryReleaseCertificationEvidence(
            name="snapshot_gate",
            passed=certified,
            severity="critical",
            message="Passed." if certified else "Failed.",
        )
    ]

    provisional = RepositoryReleaseCertification(
        schema_version=CERTIFICATION_SCHEMA_VERSION,
        repository_path="/repo",
        repository_name="repo",
        release_ready=certified,
        status="certified" if certified else "denied",
        certificate_id="",
        baseline_fingerprint="same",
        candidate_fingerprint="same",
        evidence=evidence,
        denial_reasons=[] if certified else ["snapshot_gate"],
    )

    import hashlib

    certificate_id = hashlib.sha256(
        provisional.canonical_json().encode("utf-8")
    ).hexdigest()

    return RepositoryReleaseCertification(
        schema_version=provisional.schema_version,
        repository_path=provisional.repository_path,
        repository_name=provisional.repository_name,
        release_ready=provisional.release_ready,
        status=provisional.status,
        certificate_id=certificate_id,
        baseline_fingerprint=provisional.baseline_fingerprint,
        candidate_fingerprint=provisional.candidate_fingerprint,
        evidence=provisional.evidence,
        denial_reasons=provisional.denial_reasons,
    )


def test_certification_001_certified():
    assert make_certification(True).certified is True


def test_certification_002_denied():
    assert make_certification(False).denied is True


def test_certification_003_evidence_count():
    assert make_certification(True).evidence_count == 1


def test_certification_004_passed_evidence_count():
    assert make_certification(True).passed_evidence_count == 1


def test_certification_005_failed_evidence_count():
    assert make_certification(False).failed_evidence_count == 1


def test_certification_006_critical_failure_count():
    assert make_certification(False).critical_failure_count == 1


def test_certification_007_denial_reason_count():
    assert make_certification(False).denial_reason_count == 1


def test_certification_008_certificate_valid():
    assert verify_release_certificate(
        make_certification(True)
    ) is True


def test_certification_009_builder_certifies_ready():
    readiness, baseline = make_readiness(True)

    certification = (
        RepositoryReleaseCertificationBuilder()
        .from_readiness(readiness, baseline)
    )

    assert certification.certified is True
    assert len(certification.certificate_id) == 64


def test_certification_010_builder_denies_blocked():
    readiness, baseline = make_readiness(False)

    certification = (
        RepositoryReleaseCertificationBuilder()
        .from_readiness(readiness, baseline)
    )

    assert certification.denied is True
    assert "snapshot_gate" in certification.denial_reasons


def test_certification_011_summary_certified():
    summary = RepositoryReleaseCertificationSummaryBuilder().build(
        make_certification(True)
    )

    assert summary.outcome == "release_certified"


def test_certification_012_summary_denied_critical():
    summary = RepositoryReleaseCertificationSummaryBuilder().build(
        make_certification(False)
    )

    assert summary.outcome == "certification_denied_critical"


def test_certification_013_serialize():
    response = serialize_repository_release_certification(
        make_certification(True)
    )

    assert response.certified is True
    assert response.certificate_valid is True


def test_certification_014_real_repository_certified(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    certification = RepositoryReleaseCertificationBuilder().build(
        repository_path=repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    assert certification.certified is True


def test_certification_015_changed_repository_denied(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    certification = RepositoryReleaseCertificationBuilder().build(
        repository_path=candidate_repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    assert certification.denied is True


def test_certification_016_api_certified(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    response = client.post(
        "/api/v1/repository-release-certification",
        json={
            "repository_path": str(repo),
            "baseline_json": baseline.to_json(),
            "policy": {
                "require_fingerprint_match": True
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["certified"] is True
    assert response.json()["certificate_valid"] is True


def test_certification_017_api_denied(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    response = client.post(
        "/api/v1/repository-release-certification",
        json={
            "repository_path": str(candidate_repo),
            "baseline_json": baseline.to_json(),
            "policy": {
                "require_fingerprint_match": True
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["denied"] is True


def test_certification_018_api_invalid_baseline(tmp_path):
    repo = make_repo(tmp_path / "repo")

    response = client.post(
        "/api/v1/repository-release-certification",
        json={
            "repository_path": str(repo),
            "baseline_json": "{invalid",
        },
    )

    assert response.status_code == 400


def test_certification_019_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-certification"
        in paths
    )


def test_certification_020_route_supports_post():
    route = next(
        route
        for route in app.routes
        if (
            route.path
            == "/api/v1/repository-release-certification"
        )
    )

    assert "POST" in route.methods
