from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
    RepositorySnapshotBaselineBuilder,
    RepositorySnapshotBaselineVerification,
    RepositorySnapshotBaselineVerifier,
    baseline_checksum,
)
from app.connectors.repository.repository_snapshot_baseline_summary import (
    RepositorySnapshotBaselineSummaryBuilder,
)
from app.schemas.repository_snapshot_baseline import (
    RepositorySnapshotBaselineCreateRequest,
    RepositorySnapshotBaselineCreateResponse,
    RepositorySnapshotBaselineData,
    RepositorySnapshotBaselineMetricResponse,
    RepositorySnapshotBaselineSummaryResponse,
    RepositorySnapshotBaselineVerifyRequest,
    RepositorySnapshotBaselineVerifyResponse,
)

router = APIRouter()


def serialize_repository_snapshot_baseline_data(
    baseline: RepositorySnapshotBaseline,
) -> RepositorySnapshotBaselineData:
    return RepositorySnapshotBaselineData(
        schema_version=baseline.schema_version,
        repository_name=baseline.repository_name,
        fingerprint=baseline.fingerprint,
        metrics=[
            RepositorySnapshotBaselineMetricResponse(
                name=metric.name,
                value=metric.value,
                status=metric.status,
            )
            for metric in baseline.metrics
        ],
        node_count=baseline.node_count,
        edge_count=baseline.edge_count,
        report_section_count=baseline.report_section_count,
        warning_count=baseline.warning_count,
        critical_count=baseline.critical_count,
    )


def serialize_repository_snapshot_baseline(
    baseline: RepositorySnapshotBaseline,
) -> RepositorySnapshotBaselineCreateResponse:
    summary = RepositorySnapshotBaselineSummaryBuilder().build_baseline(
        baseline
    )

    return RepositorySnapshotBaselineCreateResponse(
        baseline=serialize_repository_snapshot_baseline_data(
            baseline
        ),
        metric_count=baseline.metric_count,
        metric_names=baseline.metric_names,
        is_healthy=baseline.is_healthy,
        baseline_json=baseline.to_json(),
        checksum=baseline_checksum(baseline),
        summary=RepositorySnapshotBaselineSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


def serialize_repository_snapshot_baseline_verification(
    verification: RepositorySnapshotBaselineVerification,
) -> RepositorySnapshotBaselineVerifyResponse:
    summary = (
        RepositorySnapshotBaselineSummaryBuilder()
        .build_verification(verification)
    )

    return RepositorySnapshotBaselineVerifyResponse(
        matches=verification.matches,
        fingerprint_matches=verification.fingerprint_matches,
        difference_count=verification.difference_count,
        metric_differences=verification.metric_differences,
        baseline_fingerprint=verification.baseline.fingerprint,
        candidate_fingerprint=verification.candidate.fingerprint,
        summary=RepositorySnapshotBaselineSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-snapshot-baseline",
    response_model=RepositorySnapshotBaselineCreateResponse,
    status_code=status.HTTP_200_OK,
)
def create_repository_snapshot_baseline(
    data: RepositorySnapshotBaselineCreateRequest,
):
    try:
        baseline = RepositorySnapshotBaselineBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )

        return serialize_repository_snapshot_baseline(
            baseline
        )

    except (FileNotFoundError, NotADirectoryError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/api/v1/repository-snapshot-baseline/verify",
    response_model=RepositorySnapshotBaselineVerifyResponse,
    status_code=status.HTTP_200_OK,
)
def verify_repository_snapshot_baseline(
    data: RepositorySnapshotBaselineVerifyRequest,
):
    try:
        baseline = RepositorySnapshotBaseline.from_json(
            data.baseline_json
        )

        verification = RepositorySnapshotBaselineVerifier().verify(
            repository_path=data.repository_path,
            baseline=baseline,
            max_depth=data.max_depth,
        )

        return serialize_repository_snapshot_baseline_verification(
            verification
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
