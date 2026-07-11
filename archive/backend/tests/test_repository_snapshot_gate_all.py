from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_snapshot_gate import (
    serialize_repository_snapshot_gate_result,
)
from app.connectors.repository.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshot,
    RepositoryIntelligenceSnapshotMetric,
)
from app.connectors.repository.repository_snapshot_baseline import (
    BASELINE_SCHEMA_VERSION,
    RepositorySnapshotBaseline,
    RepositorySnapshotBaselineBuilder,
    RepositorySnapshotBaselineMetric,
    RepositorySnapshotBaselineVerification,
)
from app.connectors.repository.repository_snapshot_gate import (
    RepositorySnapshotGateEvaluator,
    RepositorySnapshotGateReason,
    RepositorySnapshotGateResult,
)
from app.connectors.repository.repository_snapshot_gate_summary import (
    RepositorySnapshotGateSummaryBuilder,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
    RepositorySnapshotPolicyEvaluation,
    RepositorySnapshotPolicyViolation,
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


def make_baseline():
    return RepositorySnapshotBaseline(
        schema_version=BASELINE_SCHEMA_VERSION,
        repository_name="repo",
        fingerprint="same",
        metrics=[
            RepositorySnapshotBaselineMetric(
                "files",
                2,
                "healthy",
            )
        ],
        node_count=10,
        edge_count=8,
        report_section_count=5,
        warning_count=0,
        critical_count=0,
    )


def make_snapshot(
    fingerprint="same",
):
    return RepositoryIntelligenceSnapshot(
        repository_path="/repo",
        repository_name="repo",
        metrics=[
            RepositoryIntelligenceSnapshotMetric(
                "files",
                2,
                "healthy",
            )
        ],
        node_count=10,
        edge_count=8,
        report_section_count=5,
        warning_count=0,
        critical_count=0,
        fingerprint=fingerprint,
    )


def make_verification(
    matches=True,
):
    return RepositorySnapshotBaselineVerification(
        baseline=make_baseline(),
        candidate=make_snapshot(
            "same" if matches else "different"
        ),
        fingerprint_matches=matches,
        metric_differences=[] if matches else [
            "metric_changed:files"
        ],
    )


def make_policy_evaluation(
    passed=True,
):
    return RepositorySnapshotPolicyEvaluation(
        repository_path="/repo",
        baseline_fingerprint="same",
        candidate_fingerprint=(
            "same" if passed else "different"
        ),
        policy=RepositorySnapshotPolicy(),
        violations=[] if passed else [
            RepositorySnapshotPolicyViolation(
                rule="require_fingerprint_match",
                subject="fingerprint",
                message="Fingerprint mismatch.",
                severity="critical",
            )
        ],
    )


def test_gate_001_passed():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(True),
        make_policy_evaluation(True),
    )
    assert result.passed is True


def test_gate_002_blocked():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(False),
        make_policy_evaluation(True),
        [
            RepositorySnapshotGateReason(
                "baseline_difference",
                "Changed.",
                "warning",
            )
        ],
    )
    assert result.blocked is True


def test_gate_003_exit_code_passed():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(True),
        make_policy_evaluation(True),
    )
    assert result.exit_code == 0


def test_gate_004_exit_code_blocked():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(False),
        make_policy_evaluation(True),
        [
            RepositorySnapshotGateReason(
                "baseline_difference",
                "Changed.",
                "warning",
            )
        ],
    )
    assert result.exit_code == 1


def test_gate_005_reason_count():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(False),
        make_policy_evaluation(True),
        [
            RepositorySnapshotGateReason(
                "baseline_difference",
                "Changed.",
                "warning",
            )
        ],
    )
    assert result.reason_count == 1


def test_gate_006_reason_codes():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(False),
        make_policy_evaluation(True),
        [
            RepositorySnapshotGateReason(
                "z",
                "Changed.",
                "warning",
            ),
            RepositorySnapshotGateReason(
                "a",
                "Changed.",
                "warning",
            ),
        ],
    )
    assert result.reason_codes == ["a", "z"]


def test_gate_007_critical_status():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(False),
        make_policy_evaluation(False),
        [
            RepositorySnapshotGateReason(
                "policy:strict",
                "Blocked.",
                "critical",
            )
        ],
    )
    assert result.status == "blocked_critical"


def test_gate_008_passed_status():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(True),
        make_policy_evaluation(True),
    )
    assert result.status == "passed"


def test_gate_009_evaluate_results_passes():
    result = RepositorySnapshotGateEvaluator().evaluate_results(
        repository_path="/repo",
        verification=make_verification(True),
        policy_evaluation=make_policy_evaluation(True),
    )
    assert result.passed is True


def test_gate_010_evaluate_results_baseline_reason():
    result = RepositorySnapshotGateEvaluator().evaluate_results(
        repository_path="/repo",
        verification=make_verification(False),
        policy_evaluation=make_policy_evaluation(True),
    )
    assert "baseline_fingerprint_mismatch" in (
        result.reason_codes
    )


def test_gate_011_evaluate_results_policy_reason():
    result = RepositorySnapshotGateEvaluator().evaluate_results(
        repository_path="/repo",
        verification=make_verification(True),
        policy_evaluation=make_policy_evaluation(False),
    )
    assert (
        "policy:require_fingerprint_match"
        in result.reason_codes
    )


def test_gate_012_summary_passed():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(True),
        make_policy_evaluation(True),
    )
    summary = RepositorySnapshotGateSummaryBuilder().build(
        result
    )
    assert summary.outcome == "gate_passed"


def test_gate_013_summary_blocked():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(False),
        make_policy_evaluation(True),
        [
            RepositorySnapshotGateReason(
                "baseline_difference",
                "Changed.",
                "warning",
            )
        ],
    )
    summary = RepositorySnapshotGateSummaryBuilder().build(
        result
    )
    assert summary.outcome == "gate_blocked"


def test_gate_014_summary_critical():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(False),
        make_policy_evaluation(False),
        [
            RepositorySnapshotGateReason(
                "policy:strict",
                "Blocked.",
                "critical",
            )
        ],
    )
    summary = RepositorySnapshotGateSummaryBuilder().build(
        result
    )
    assert summary.outcome == "gate_blocked_critical"


def test_gate_015_serialize():
    result = RepositorySnapshotGateResult(
        "/repo",
        make_verification(True),
        make_policy_evaluation(True),
    )
    response = serialize_repository_snapshot_gate_result(
        result
    )
    assert response.passed is True
    assert response.exit_code == 0


def test_gate_016_real_repository_passes(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    result = RepositorySnapshotGateEvaluator().evaluate(
        repository_path=repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    assert result.passed is True


def test_gate_017_changed_repository_blocked(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    result = RepositorySnapshotGateEvaluator().evaluate(
        repository_path=candidate_repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    assert result.blocked is True


def test_gate_018_changed_repository_exit_code(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    result = RepositorySnapshotGateEvaluator().evaluate(
        repository_path=candidate_repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    assert result.exit_code == 1


def test_gate_019_api_passes(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    response = client.post(
        "/api/v1/repository-snapshot-gate",
        json={
            "repository_path": str(repo),
            "baseline_json": baseline.to_json(),
            "policy": {
                "require_fingerprint_match": True
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["passed"] is True


def test_gate_020_api_blocks_changed(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    response = client.post(
        "/api/v1/repository-snapshot-gate",
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
    assert response.json()["exit_code"] == 1


def test_gate_021_api_invalid_baseline(tmp_path):
    repo = make_repo(tmp_path / "repo")

    response = client.post(
        "/api/v1/repository-snapshot-gate",
        json={
            "repository_path": str(repo),
            "baseline_json": "{invalid",
        },
    )

    assert response.status_code == 400


def test_gate_022_api_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-snapshot-gate",
        json={
            "repository_path": str(tmp_path / "missing"),
            "baseline_json": make_baseline().to_json(),
        },
    )

    assert response.status_code == 400


def test_gate_023_api_empty_path():
    response = client.post(
        "/api/v1/repository-snapshot-gate",
        json={
            "repository_path": "",
            "baseline_json": make_baseline().to_json(),
        },
    )

    assert response.status_code == 422


def test_gate_024_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-snapshot-gate" in paths


def test_gate_025_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path == "/api/v1/repository-snapshot-gate"
    )
    assert "POST" in route.methods
