from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_audit_ledger_snapshot_comparison import (
    RepositoryReleaseAuditLedgerSnapshotComparison,
    RepositoryReleaseAuditLedgerSnapshotComparisonBuilder,
)
from app.connectors.repository.repository_release_audit_ledger_snapshot_comparison_summary import (
    RepositoryReleaseAuditLedgerSnapshotComparisonSummaryBuilder,
)
from app.schemas.repository_release_audit_ledger_snapshot_comparison import (
    RepositoryReleaseAuditLedgerSnapshotComparisonRequest,
    RepositoryReleaseAuditLedgerSnapshotComparisonResponse,
    RepositoryReleaseAuditLedgerSnapshotComparisonSummaryResponse,
)

router = APIRouter()


def serialize_ledger_snapshot_comparison(
    comparison: RepositoryReleaseAuditLedgerSnapshotComparison,
) -> RepositoryReleaseAuditLedgerSnapshotComparisonResponse:
    summary = (
        RepositoryReleaseAuditLedgerSnapshotComparisonSummaryBuilder()
        .build(comparison)
    )

    return RepositoryReleaseAuditLedgerSnapshotComparisonResponse(
        baseline_snapshot_id=(
            comparison.baseline_snapshot_id
        ),
        candidate_snapshot_id=(
            comparison.candidate_snapshot_id
        ),
        baseline_ledger_id=comparison.baseline_ledger_id,
        candidate_ledger_id=(
            comparison.candidate_ledger_id
        ),
        baseline_valid=(
            comparison.baseline_verification.valid
        ),
        candidate_valid=(
            comparison.candidate_verification.valid
        ),
        baseline_accepted=(
            comparison.baseline_verification.accepted
        ),
        candidate_accepted=(
            comparison.candidate_verification.accepted
        ),
        baseline_entry_count=(
            comparison.baseline_entry_count
        ),
        candidate_entry_count=(
            comparison.candidate_entry_count
        ),
        entry_count_delta=comparison.entry_count_delta,
        added_bundle_ids=comparison.added_bundle_ids,
        removed_bundle_ids=comparison.removed_bundle_ids,
        append_only=comparison.append_only,
        history_rewritten=comparison.history_rewritten,
        acceptance_regression=(
            comparison.acceptance_regression
        ),
        acceptance_improvement=(
            comparison.acceptance_improvement
        ),
        ledger_changed=comparison.ledger_changed,
        snapshots_identical=comparison.snapshots_identical,
        changed=comparison.changed,
        safe_progression=comparison.safe_progression,
        status=comparison.status,
        summary=(
            RepositoryReleaseAuditLedgerSnapshotComparisonSummaryResponse(
                outcome=summary.outcome,
                message=summary.message,
                action_required=summary.action_required,
            )
        ),
    )


@router.post(
    "/api/v1/repository-release-audit-ledger-snapshot-comparison",
    response_model=(
        RepositoryReleaseAuditLedgerSnapshotComparisonResponse
    ),
    status_code=status.HTTP_200_OK,
)
def compare_repository_release_audit_ledger_snapshots(
    data: RepositoryReleaseAuditLedgerSnapshotComparisonRequest,
):
    try:
        comparison = (
            RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
            .build(
                baseline_snapshot_json=(
                    data.baseline_snapshot_json
                ),
                candidate_snapshot_json=(
                    data.candidate_snapshot_json
                ),
                require_accepted=data.require_accepted,
            )
        )

        return serialize_ledger_snapshot_comparison(
            comparison
        )

    except (
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
