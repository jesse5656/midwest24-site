from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
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
)
from app.schemas.repository_snapshot_gate import (
    RepositorySnapshotGateReasonResponse,
    RepositorySnapshotGateRequest,
    RepositorySnapshotGateResponse,
    RepositorySnapshotGateSummaryResponse,
)

router = APIRouter()


def serialize_repository_snapshot_gate_reason(
    reason: RepositorySnapshotGateReason,
) -> RepositorySnapshotGateReasonResponse:
    return RepositorySnapshotGateReasonResponse(
        code=reason.code,
        message=reason.message,
        severity=reason.severity,
    )


def serialize_repository_snapshot_gate_result(
    result: RepositorySnapshotGateResult,
) -> RepositorySnapshotGateResponse:
    summary = RepositorySnapshotGateSummaryBuilder().build(
        result
    )

    return RepositorySnapshotGateResponse(
        repository_path=result.repository_path,
        passed=result.passed,
        blocked=result.blocked,
        status=result.status,
        exit_code=result.exit_code,
        reason_count=result.reason_count,
        critical_reason_count=result.critical_reason_count,
        warning_reason_count=result.warning_reason_count,
        reason_codes=result.reason_codes,
        reasons=[
            serialize_repository_snapshot_gate_reason(reason)
            for reason in result.reasons
        ],
        baseline_matches=(
            result.baseline_verification.matches
        ),
        baseline_fingerprint_matches=(
            result.baseline_verification.fingerprint_matches
        ),
        baseline_difference_count=(
            result.baseline_verification.difference_count
        ),
        policy_passed=result.policy_evaluation.passed,
        policy_violation_count=(
            result.policy_evaluation.violation_count
        ),
        summary=RepositorySnapshotGateSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-snapshot-gate",
    response_model=RepositorySnapshotGateResponse,
    status_code=status.HTTP_200_OK,
)
def evaluate_repository_snapshot_gate(
    data: RepositorySnapshotGateRequest,
):
    try:
        baseline = RepositorySnapshotBaseline.from_json(
            data.baseline_json
        )

        policy = RepositorySnapshotPolicy(
            require_fingerprint_match=(
                data.policy.require_fingerprint_match
            ),
            allow_added_metrics=data.policy.allow_added_metrics,
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

        result = RepositorySnapshotGateEvaluator().evaluate(
            repository_path=data.repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=data.max_depth,
        )

        return serialize_repository_snapshot_gate_result(
            result
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
