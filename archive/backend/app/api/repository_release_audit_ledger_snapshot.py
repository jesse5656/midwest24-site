from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_audit_ledger_snapshot import (
    RepositoryReleaseAuditLedgerSnapshot,
    RepositoryReleaseAuditLedgerSnapshotBuilder,
    RepositoryReleaseAuditLedgerSnapshotEntry,
    verify_release_audit_ledger_snapshot,
)
from app.connectors.repository.repository_release_audit_ledger_snapshot_summary import (
    RepositoryReleaseAuditLedgerSnapshotSummaryBuilder,
)
from app.schemas.repository_release_audit_ledger_snapshot import (
    RepositoryReleaseAuditLedgerSnapshotEntryResponse,
    RepositoryReleaseAuditLedgerSnapshotRequest,
    RepositoryReleaseAuditLedgerSnapshotResponse,
    RepositoryReleaseAuditLedgerSnapshotSummaryResponse,
)

router = APIRouter()


def serialize_release_audit_ledger_snapshot_entry(
    entry: RepositoryReleaseAuditLedgerSnapshotEntry,
) -> RepositoryReleaseAuditLedgerSnapshotEntryResponse:
    return RepositoryReleaseAuditLedgerSnapshotEntryResponse(
        sequence=entry.sequence,
        bundle_id=entry.bundle_id,
        repository_name=entry.repository_name,
        accepted=entry.accepted,
        entry_hash=entry.entry_hash,
    )


def serialize_release_audit_ledger_snapshot(
    snapshot: RepositoryReleaseAuditLedgerSnapshot,
) -> RepositoryReleaseAuditLedgerSnapshotResponse:
    summary = (
        RepositoryReleaseAuditLedgerSnapshotSummaryBuilder()
        .build(snapshot)
    )

    return RepositoryReleaseAuditLedgerSnapshotResponse(
        schema_version=snapshot.schema_version,
        snapshot_id=snapshot.snapshot_id,
        snapshot_valid=verify_release_audit_ledger_snapshot(
            snapshot
        ),
        ledger_id=snapshot.ledger_id,
        ledger_integrity_valid=(
            snapshot.ledger_integrity_valid
        ),
        ledger_chain_valid=snapshot.ledger_chain_valid,
        ledger_accepted=snapshot.ledger_accepted,
        accepted=snapshot.accepted,
        rejected=snapshot.rejected,
        status=snapshot.status,
        entry_count=snapshot.entry_count,
        accepted_entry_count=(
            snapshot.accepted_entry_count
        ),
        rejected_entry_count=(
            snapshot.rejected_entry_count
        ),
        latest_entry_hash=snapshot.latest_entry_hash,
        repository_names=snapshot.repository_names,
        repository_count=snapshot.repository_count,
        entries=[
            serialize_release_audit_ledger_snapshot_entry(
                entry
            )
            for entry in snapshot.entries
        ],
        issue_codes=snapshot.issue_codes,
        issue_count=snapshot.issue_count,
        snapshot_json=snapshot.as_json(),
        snapshot_markdown=snapshot.as_markdown(),
        summary=(
            RepositoryReleaseAuditLedgerSnapshotSummaryResponse(
                outcome=summary.outcome,
                message=summary.message,
                action_required=summary.action_required,
            )
        ),
    )


@router.post(
    "/api/v1/repository-release-audit-ledger-snapshot",
    response_model=(
        RepositoryReleaseAuditLedgerSnapshotResponse
    ),
    status_code=status.HTTP_200_OK,
)
def create_repository_release_audit_ledger_snapshot(
    data: RepositoryReleaseAuditLedgerSnapshotRequest,
):
    try:
        snapshot = (
            RepositoryReleaseAuditLedgerSnapshotBuilder()
            .build(
                ledger_json=data.ledger_json,
                require_all_accepted=(
                    data.require_all_accepted
                ),
            )
        )

        return serialize_release_audit_ledger_snapshot(
            snapshot
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
