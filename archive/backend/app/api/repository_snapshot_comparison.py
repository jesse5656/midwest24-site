from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_snapshot_comparison import (
    RepositorySnapshotComparison,
    RepositorySnapshotComparisonBuilder,
    RepositorySnapshotMetricChange,
)
from app.connectors.repository.repository_snapshot_comparison_summary import (
    RepositorySnapshotComparisonSummaryBuilder,
)
from app.schemas.repository_snapshot_comparison import (
    RepositorySnapshotComparisonRequest,
    RepositorySnapshotComparisonResponse,
    RepositorySnapshotComparisonSummaryResponse,
    RepositorySnapshotMetricChangeResponse,
)

router = APIRouter()


def serialize_repository_snapshot_metric_change(
    change: RepositorySnapshotMetricChange,
) -> RepositorySnapshotMetricChangeResponse:
    return RepositorySnapshotMetricChangeResponse(
        name=change.name,
        baseline_value=change.baseline_value,
        candidate_value=change.candidate_value,
        delta=change.delta,
        change_type=change.change_type,
    )


def serialize_repository_snapshot_comparison(
    comparison: RepositorySnapshotComparison,
) -> RepositorySnapshotComparisonResponse:
    summary = RepositorySnapshotComparisonSummaryBuilder().build(
        comparison
    )

    return RepositorySnapshotComparisonResponse(
        baseline_repository_path=(
            comparison.baseline_repository_path
        ),
        candidate_repository_path=(
            comparison.candidate_repository_path
        ),
        baseline_fingerprint=comparison.baseline_fingerprint,
        candidate_fingerprint=comparison.candidate_fingerprint,
        fingerprints_match=comparison.fingerprints_match,
        has_changes=comparison.has_changes,
        metric_changes=[
            serialize_repository_snapshot_metric_change(change)
            for change in comparison.metric_changes
        ],
        metric_change_count=comparison.metric_change_count,
        increased_metric_count=comparison.increased_metric_count,
        decreased_metric_count=comparison.decreased_metric_count,
        added_metric_count=comparison.added_metric_count,
        removed_metric_count=comparison.removed_metric_count,
        unchanged_metric_count=comparison.unchanged_metric_count,
        changed_metric_names=comparison.changed_metric_names,
        node_delta=comparison.node_delta,
        edge_delta=comparison.edge_delta,
        report_section_delta=comparison.report_section_delta,
        warning_delta=comparison.warning_delta,
        critical_delta=comparison.critical_delta,
        summary=RepositorySnapshotComparisonSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-snapshot-comparison",
    response_model=RepositorySnapshotComparisonResponse,
    status_code=status.HTTP_200_OK,
)
def compare_repository_snapshots(
    data: RepositorySnapshotComparisonRequest,
):
    try:
        comparison = RepositorySnapshotComparisonBuilder().compare(
            baseline_repository_path=(
                data.baseline_repository_path
            ),
            candidate_repository_path=(
                data.candidate_repository_path
            ),
            max_depth=data.max_depth,
        )

        return serialize_repository_snapshot_comparison(
            comparison
        )

    except (FileNotFoundError, NotADirectoryError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
