from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_readiness import (
    serialize_repository_release_readiness,
)
from app.connectors.repository.repository_intelligence_dashboard import (
    RepositoryIntelligenceDashboard,
    RepositoryIntelligenceMetric,
)
from app.connectors.repository.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshot,
)
from app.connectors.repository.repository_release_readiness import (
    RepositoryReleaseReadiness,
    RepositoryReleaseReadinessCheck,
    RepositoryReleaseReadinessEvaluator,
)
from app.connectors.repository.repository_release_readiness_summary import (
    RepositoryReleaseReadinessSummaryBuilder,
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


def make_repo(root: Path, changed: bool = False) -> Path:
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


def make_gate(passed: bool = True):
    snapshot = RepositoryIntelligenceSnapshot(
        repository_path="/repo",
        repository_name="repo",
        fingerprint="same",
    )

    verification = RepositorySnapshotBaselineVerification(
        baseline=RepositorySnapshotBaselineBuilder().from_snapshot(
            snapshot
        ),
        candidate=snapshot,
        fingerprint_matches=passed,
        metric_differences=[] if passed else ["changed"],
    )

    policy = RepositorySnapshotPolicyEvaluation(
        repository_path="/repo",
        baseline_fingerprint="same",
        candidate_fingerprint="same",
        policy=RepositorySnapshotPolicy(),
        violations=[],
    )

    return RepositorySnapshotGateResult(
        repository_path="/repo",
        baseline_verification=verification,
        policy_evaluation=policy,
        reasons=[],
    )


def make_dashboard(healthy: bool = True):
    return RepositoryIntelligenceDashboard(
        repository_path="/repo",
        repository_name="repo",
        metrics=[
            RepositoryIntelligenceMetric(
                "knowledge_graph_nodes",
                1 if healthy else 0,
                "healthy" if healthy else "warning",
            ),
            RepositoryIntelligenceMetric(
                "search_documents",
                1,
                "healthy",
            ),
            RepositoryIntelligenceMetric(
                "architecture_findings",
                1,
                "healthy",
            ),
            RepositoryIntelligenceMetric(
                "summary_sections",
                1,
                "healthy",
            ),
        ],
        warnings=[] if healthy else ["graph"],
    )


def make_readiness(
    checks=None,
    healthy=True,
):
    return RepositoryReleaseReadiness(
        repository_path="/repo",
        repository_name="repo",
        gate=make_gate(True),
        dashboard=make_dashboard(healthy),
        checks=checks or [],
    )


def test_readiness_001_check_count():
    readiness = make_readiness(
        [
            RepositoryReleaseReadinessCheck(
                "gate",
                True,
                "critical",
                "Passed.",
            )
        ]
    )
    assert readiness.check_count == 1


def test_readiness_002_passed_count():
    readiness = make_readiness(
        [
            RepositoryReleaseReadinessCheck(
                "gate",
                True,
                "critical",
                "Passed.",
            )
        ]
    )
    assert readiness.passed_check_count == 1


def test_readiness_003_failed_count():
    readiness = make_readiness(
        [
            RepositoryReleaseReadinessCheck(
                "gate",
                False,
                "critical",
                "Failed.",
            )
        ]
    )
    assert readiness.failed_check_count == 1


def test_readiness_004_critical_failures():
    readiness = make_readiness(
        [
            RepositoryReleaseReadinessCheck(
                "gate",
                False,
                "critical",
                "Failed.",
            )
        ]
    )
    assert readiness.critical_failure_count == 1


def test_readiness_005_failed_names():
    readiness = make_readiness(
        [
            RepositoryReleaseReadinessCheck(
                "gate",
                False,
                "critical",
                "Failed.",
            )
        ]
    )
    assert readiness.failed_check_names == ["gate"]


def test_readiness_006_release_ready():
    readiness = make_readiness(
        [
            RepositoryReleaseReadinessCheck(
                "gate",
                True,
                "critical",
                "Passed.",
            )
        ]
    )
    assert readiness.release_ready is True
    assert readiness.exit_code == 0


def test_readiness_007_blocked():
    readiness = make_readiness(
        [
            RepositoryReleaseReadinessCheck(
                "gate",
                False,
                "critical",
                "Failed.",
            )
        ]
    )
    assert readiness.blocked is True
    assert readiness.status == "blocked_critical"


def test_readiness_008_builder_passes(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    readiness = RepositoryReleaseReadinessEvaluator().evaluate(
        repository_path=repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    assert readiness.release_ready is True
    assert readiness.check_count == 6


def test_readiness_009_builder_blocks_changed(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    readiness = RepositoryReleaseReadinessEvaluator().evaluate(
        repository_path=candidate_repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    assert readiness.blocked is True


def test_readiness_010_summary_ready():
    readiness = make_readiness(
        [
            RepositoryReleaseReadinessCheck(
                "gate",
                True,
                "critical",
                "Passed.",
            )
        ]
    )

    summary = RepositoryReleaseReadinessSummaryBuilder().build(
        readiness
    )

    assert summary.outcome == "release_ready"


def test_readiness_011_summary_critical():
    readiness = make_readiness(
        [
            RepositoryReleaseReadinessCheck(
                "gate",
                False,
                "critical",
                "Failed.",
            )
        ]
    )

    summary = RepositoryReleaseReadinessSummaryBuilder().build(
        readiness
    )

    assert summary.outcome == "release_blocked_critical"


def test_readiness_012_serialize():
    readiness = make_readiness(
        [
            RepositoryReleaseReadinessCheck(
                "gate",
                True,
                "critical",
                "Passed.",
            )
        ]
    )

    response = serialize_repository_release_readiness(
        readiness
    )

    assert response.release_ready is True
    assert response.exit_code == 0


def test_readiness_013_api_ready(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    response = client.post(
        "/api/v1/repository-release-readiness",
        json={
            "repository_path": str(repo),
            "baseline_json": baseline.to_json(),
            "policy": {
                "require_fingerprint_match": True
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["release_ready"] is True


def test_readiness_014_api_changed_blocked(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    response = client.post(
        "/api/v1/repository-release-readiness",
        json={
            "repository_path": str(candidate_repo),
            "baseline_json": baseline.to_json(),
            "policy": {
                "require_fingerprint_match": True
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["blocked"] is True


def test_readiness_015_api_invalid_baseline(tmp_path):
    repo = make_repo(tmp_path / "repo")

    response = client.post(
        "/api/v1/repository-release-readiness",
        json={
            "repository_path": str(repo),
            "baseline_json": "{invalid",
        },
    )

    assert response.status_code == 400


def test_readiness_016_api_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-release-readiness",
        json={
            "repository_path": str(tmp_path / "missing"),
            "baseline_json": "{}",
        },
    )

    assert response.status_code == 400


def test_readiness_017_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-release-readiness" in paths


def test_readiness_018_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path == "/api/v1/repository-release-readiness"
    )
    assert "POST" in route.methods
