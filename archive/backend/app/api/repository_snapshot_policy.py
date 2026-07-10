from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
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
from app.schemas.repository_snapshot_policy import (
    RepositorySnapshotPolicyRequest,
    RepositorySnapshotPolicyResponse,
    RepositorySnapshotPolicySummaryResponse,
    RepositorySnapshotPolicyViolationResponse,
)

router = APIRouter()


def serialize_repository_snapshot_policy_violation(
    violation: RepositorySnapshotPolicyViolation,
) -> RepositorySnapshotPolicyViolationResponse:
    return RepositorySnapshotPolicyViolationResponse(
        rule=violation.rule,
        subject=violation.subject,
        message=violation.message,
        severity=violation.severity,
    )


def serialize_repository_snapshot_policy_evaluation(
    evaluation: RepositorySnapshotPolicyEvaluation,
) -> RepositorySnapshotPolicyResponse:
    summary = RepositorySnapshotPolicySummaryBuilder().build(
        evaluation
    )

    return RepositorySnapshotPolicyResponse(
        repository_path=evaluation.repository_path,
        baseline_fingerprint=evaluation.baseline_fingerprint,
        candidate_fingerprint=evaluation.candidate_fingerprint,
        passed=evaluation.passed,
        violation_count=evaluation.violation_count,
        failed_rules=evaluation.failed_rules,
        critical_violation_count=(
            evaluation.critical_violation_count
        ),
        error_violation_count=evaluation.error_violation_count,
        violations=[
            serialize_repository_snapshot_policy_violation(
                violation
            )
            for violation in evaluation.violations
        ],
        summary=RepositorySnapshotPolicySummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-snapshot-policy",
    response_model=RepositorySnapshotPolicyResponse,
    status_code=status.HTTP_200_OK,
)
def evaluate_repository_snapshot_policy(
    data: RepositorySnapshotPolicyRequest,
):
    try:
        baseline = RepositorySnapshotBaseline.from_json(
            data.baseline_json
        )

        policy = RepositorySnapshotPolicy(
            require_fingerprint_match=(
                data.policy.require_fingerprint_match
            ),
            allow_added_metrics=(
                data.policy.allow_added_metrics
            ),
            allow_removed_metrics=(
                data.policy.allow_removed_metrics
            ),
            max_warning_delta=data.policy.max_warning_delta,
            max_critical_delta=data.policy.max_critical_delta,
            max_node_decrease=data.policy.max_node_decrease,
            max_edge_decrease=data.policy.max_edge_decrease,
            max_metric_decrease=(
                data.policy.max_metric_decrease
            ),
        )

        evaluation = RepositorySnapshotPolicyEvaluator().evaluate(
            repository_path=data.repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=data.max_depth,
        )

        return serialize_repository_snapshot_policy_evaluation(
            evaluation
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
