from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshot,
    RepositoryIntelligenceSnapshotBuilder,
    RepositoryIntelligenceSnapshotMetric,
)
from app.connectors.repository.repository_intelligence_snapshot_summary import (
    RepositoryIntelligenceSnapshotSummaryBuilder,
)
from app.schemas.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshotMetricResponse,
    RepositoryIntelligenceSnapshotRequest,
    RepositoryIntelligenceSnapshotResponse,
    RepositoryIntelligenceSnapshotSummaryResponse,
)

router = APIRouter()


def serialize_repository_intelligence_snapshot_metric(
    metric: RepositoryIntelligenceSnapshotMetric,
) -> RepositoryIntelligenceSnapshotMetricResponse:
    return RepositoryIntelligenceSnapshotMetricResponse(
        name=metric.name,
        value=metric.value,
        status=metric.status,
    )


def serialize_repository_intelligence_snapshot(
    snapshot: RepositoryIntelligenceSnapshot,
) -> RepositoryIntelligenceSnapshotResponse:
    summary = RepositoryIntelligenceSnapshotSummaryBuilder().build(
        snapshot
    )

    return RepositoryIntelligenceSnapshotResponse(
        repository_path=snapshot.repository_path,
        repository_name=snapshot.repository_name,
        metrics=[
            serialize_repository_intelligence_snapshot_metric(
                metric
            )
            for metric in snapshot.metrics
        ],
        metric_count=snapshot.metric_count,
        metric_names=snapshot.metric_names,
        node_count=snapshot.node_count,
        edge_count=snapshot.edge_count,
        report_section_count=snapshot.report_section_count,
        warning_count=snapshot.warning_count,
        critical_count=snapshot.critical_count,
        is_healthy=snapshot.is_healthy,
        fingerprint=snapshot.fingerprint,
        canonical_json=snapshot.canonical_json(),
        summary=RepositoryIntelligenceSnapshotSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-intelligence-snapshot",
    response_model=RepositoryIntelligenceSnapshotResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_intelligence_snapshot(
    data: RepositoryIntelligenceSnapshotRequest,
):
    try:
        snapshot = RepositoryIntelligenceSnapshotBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )

        return serialize_repository_intelligence_snapshot(
            snapshot
        )

    except (FileNotFoundError, NotADirectoryError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
