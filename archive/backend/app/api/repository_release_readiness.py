from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_readiness import (
    RepositoryReleaseReadiness,
    RepositoryReleaseReadinessCheck,
    RepositoryReleaseReadinessEvaluator,
)
from app.connectors.repository.repository_release_readiness_summary import (
    RepositoryReleaseReadinessSummaryBuilder,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)
from app.schemas.repository_release_readiness import (
    RepositoryReleaseReadinessCheckResponse,
    RepositoryReleaseReadinessRequest,
    RepositoryReleaseReadinessResponse,
    RepositoryReleaseReadinessSummaryResponse,
)

router = APIRouter()


def serialize_repository_release_readiness_check(
    check: RepositoryReleaseReadinessCheck,
) -> RepositoryReleaseReadinessCheckResponse:
    return RepositoryReleaseReadinessCheckResponse(
        name=check.name,
        passed=check.passed,
        severity=check.severity,
        message=check.message,
    )


def serialize_repository_release_readiness(
    readiness: RepositoryReleaseReadiness,
) -> RepositoryReleaseReadinessResponse:
    summary = RepositoryReleaseReadinessSummaryBuilder().build(
        readiness
    )

    return RepositoryReleaseReadinessResponse(
        repository_path=readiness.repository_path,
        repository_name=readiness.repository_name,
        release_ready=readiness.release_ready,
        blocked=readiness.blocked,
        status=readiness.status,
        exit_code=readiness.exit_code,
        checks=[
            serialize_repository_release_readiness_check(check)
            for check in readiness.checks
        ],
        check_count=readiness.check_count,
        passed_check_count=readiness.passed_check_count,
        failed_check_count=readiness.failed_check_count,
        critical_failure_count=readiness.critical_failure_count,
        warning_failure_count=readiness.warning_failure_count,
        failed_check_names=readiness.failed_check_names,
        gate_passed=readiness.gate.passed,
        gate_reason_count=readiness.gate.reason_count,
        dashboard_healthy=readiness.dashboard.is_healthy,
        dashboard_warning_count=readiness.dashboard.warning_count,
        summary=RepositoryReleaseReadinessSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-release-readiness",
    response_model=RepositoryReleaseReadinessResponse,
    status_code=status.HTTP_200_OK,
)
def evaluate_repository_release_readiness(
    data: RepositoryReleaseReadinessRequest,
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
            max_metric_decrease=data.policy.max_metric_decrease,
        )

        readiness = RepositoryReleaseReadinessEvaluator().evaluate(
            repository_path=data.repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=data.max_depth,
        )

        return serialize_repository_release_readiness(
            readiness
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
