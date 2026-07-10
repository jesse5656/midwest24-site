from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_snapshot_policy import (
    serialize_repository_snapshot_policy_evaluation,
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
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
    RepositorySnapshotPolicyEvaluation,
    RepositorySnapshotPolicyEvaluator,
    RepositorySnapshotPolicyViolation,
)
from app.connectors.repository.repository_snapshot_policy_summary import (
    RepositorySnapshotPolicySummaryBuilder,
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
                4,
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
    metric_value=4,
    node_count=10,
    edge_count=8,
    warning_count=0,
    critical_count=0,
):
    return RepositoryIntelligenceSnapshot(
        repository_path="/repo",
        repository_name="repo",
        metrics=[
            RepositoryIntelligenceSnapshotMetric(
                "files",
                metric_value,
                "healthy",
            )
        ],
        node_count=node_count,
        edge_count=edge_count,
        report_section_count=5,
        warning_count=warning_count,
        critical_count=critical_count,
        fingerprint=fingerprint,
    )


def test_policy_001_empty_evaluation_passes():
    evaluation = RepositorySnapshotPolicyEvaluation(
        "/repo",
        "a",
        "a",
        RepositorySnapshotPolicy(),
    )
    assert evaluation.passed is True


def test_policy_002_violation_count():
    evaluation = RepositorySnapshotPolicyEvaluation(
        "/repo",
        "a",
        "b",
        RepositorySnapshotPolicy(),
        [
            RepositorySnapshotPolicyViolation(
                "rule",
                "subject",
                "message",
            )
        ],
    )
    assert evaluation.violation_count == 1


def test_policy_003_failed_rules():
    evaluation = RepositorySnapshotPolicyEvaluation(
        "/repo",
        "a",
        "b",
        RepositorySnapshotPolicy(),
        [
            RepositorySnapshotPolicyViolation(
                "rule_b",
                "subject",
                "message",
            ),
            RepositorySnapshotPolicyViolation(
                "rule_a",
                "subject",
                "message",
            ),
        ],
    )
    assert evaluation.failed_rules == ["rule_a", "rule_b"]


def test_policy_004_exact_match_passes():
    evaluation = RepositorySnapshotPolicyEvaluator().evaluate_snapshot(
        candidate=make_snapshot(),
        baseline=make_baseline(),
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )
    assert evaluation.passed is True


def test_policy_005_fingerprint_mismatch():
    evaluation = RepositorySnapshotPolicyEvaluator().evaluate_snapshot(
        candidate=make_snapshot(fingerprint="different"),
        baseline=make_baseline(),
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )
    assert "require_fingerprint_match" in evaluation.failed_rules


def test_policy_006_warning_delta():
    evaluation = RepositorySnapshotPolicyEvaluator().evaluate_snapshot(
        candidate=make_snapshot(warning_count=2),
        baseline=make_baseline(),
        policy=RepositorySnapshotPolicy(
            max_warning_delta=1
        ),
    )
    assert "max_warning_delta" in evaluation.failed_rules


def test_policy_007_critical_delta():
    evaluation = RepositorySnapshotPolicyEvaluator().evaluate_snapshot(
        candidate=make_snapshot(critical_count=1),
        baseline=make_baseline(),
        policy=RepositorySnapshotPolicy(),
    )
    assert "max_critical_delta" in evaluation.failed_rules


def test_policy_008_node_decrease():
    evaluation = RepositorySnapshotPolicyEvaluator().evaluate_snapshot(
        candidate=make_snapshot(node_count=8),
        baseline=make_baseline(),
        policy=RepositorySnapshotPolicy(
            max_node_decrease=1
        ),
    )
    assert "max_node_decrease" in evaluation.failed_rules


def test_policy_009_edge_decrease():
    evaluation = RepositorySnapshotPolicyEvaluator().evaluate_snapshot(
        candidate=make_snapshot(edge_count=5),
        baseline=make_baseline(),
        policy=RepositorySnapshotPolicy(
            max_edge_decrease=2
        ),
    )
    assert "max_edge_decrease" in evaluation.failed_rules


def test_policy_010_metric_decrease():
    evaluation = RepositorySnapshotPolicyEvaluator().evaluate_snapshot(
        candidate=make_snapshot(metric_value=2),
        baseline=make_baseline(),
        policy=RepositorySnapshotPolicy(
            max_metric_decrease=1
        ),
    )
    assert "max_metric_decrease" in evaluation.failed_rules


def test_policy_011_metric_decrease_allowed():
    evaluation = RepositorySnapshotPolicyEvaluator().evaluate_snapshot(
        candidate=make_snapshot(metric_value=3),
        baseline=make_baseline(),
        policy=RepositorySnapshotPolicy(
            max_metric_decrease=1
        ),
    )
    assert evaluation.passed is True


def test_policy_012_summary_passed():
    evaluation = RepositorySnapshotPolicyEvaluation(
        "/repo",
        "a",
        "a",
        RepositorySnapshotPolicy(),
    )
    summary = RepositorySnapshotPolicySummaryBuilder().build(
        evaluation
    )
    assert summary.outcome == "policy_passed"


def test_policy_013_summary_failed():
    evaluation = RepositorySnapshotPolicyEvaluation(
        "/repo",
        "a",
        "b",
        RepositorySnapshotPolicy(),
        [
            RepositorySnapshotPolicyViolation(
                "rule",
                "subject",
                "message",
            )
        ],
    )
    summary = RepositorySnapshotPolicySummaryBuilder().build(
        evaluation
    )
    assert summary.outcome == "policy_failed"


def test_policy_014_summary_critical():
    evaluation = RepositorySnapshotPolicyEvaluation(
        "/repo",
        "a",
        "b",
        RepositorySnapshotPolicy(),
        [
            RepositorySnapshotPolicyViolation(
                "rule",
                "subject",
                "message",
                "critical",
            )
        ],
    )
    summary = RepositorySnapshotPolicySummaryBuilder().build(
        evaluation
    )
    assert summary.outcome == "critical_policy_failure"


def test_policy_015_serialize():
    response = serialize_repository_snapshot_policy_evaluation(
        RepositorySnapshotPolicyEvaluation(
            "/repo",
            "a",
            "a",
            RepositorySnapshotPolicy(),
        )
    )
    assert response.passed is True
    assert response.violation_count == 0


def test_policy_016_real_repository_passes(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    evaluation = RepositorySnapshotPolicyEvaluator().evaluate(
        repository_path=repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    assert evaluation.passed is True


def test_policy_017_changed_repository_fails_strict(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    evaluation = RepositorySnapshotPolicyEvaluator().evaluate(
        repository_path=candidate_repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )

    assert evaluation.passed is False


def test_policy_018_api_passes(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    response = client.post(
        "/api/v1/repository-snapshot-policy",
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


def test_policy_019_api_changed_fails(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    response = client.post(
        "/api/v1/repository-snapshot-policy",
        json={
            "repository_path": str(candidate_repo),
            "baseline_json": baseline.to_json(),
            "policy": {
                "require_fingerprint_match": True
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["passed"] is False


def test_policy_020_api_invalid_baseline(tmp_path):
    repo = make_repo(tmp_path / "repo")

    response = client.post(
        "/api/v1/repository-snapshot-policy",
        json={
            "repository_path": str(repo),
            "baseline_json": "{invalid",
        },
    )

    assert response.status_code == 400


def test_policy_021_api_missing_path(tmp_path):
    baseline = make_baseline()

    response = client.post(
        "/api/v1/repository-snapshot-policy",
        json={
            "repository_path": str(tmp_path / "missing"),
            "baseline_json": baseline.to_json(),
        },
    )

    assert response.status_code == 400


def test_policy_022_api_rejects_negative_tolerance(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    response = client.post(
        "/api/v1/repository-snapshot-policy",
        json={
            "repository_path": str(repo),
            "baseline_json": baseline.to_json(),
            "policy": {
                "max_warning_delta": -1
            },
        },
    )

    assert response.status_code == 422


def test_policy_023_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-snapshot-policy" in paths


def test_policy_024_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path == "/api/v1/repository-snapshot-policy"
    )
    assert "POST" in route.methods
