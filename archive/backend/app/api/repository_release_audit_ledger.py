from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_audit_ledger import (
    RepositoryReleaseAuditLedger,
    RepositoryReleaseAuditLedgerBuilder,
    RepositoryReleaseAuditLedgerEntry,
    RepositoryReleaseAuditLedgerVerifier,
)
from app.connectors.repository.repository_release_audit_ledger_summary import (
    RepositoryReleaseAuditLedgerSummaryBuilder,
)
from app.schemas.repository_release_audit_ledger import (
    RepositoryReleaseAuditLedgerEntryResponse,
    RepositoryReleaseAuditLedgerRequest,
    RepositoryReleaseAuditLedgerResponse,
    RepositoryReleaseAuditLedgerSummaryResponse,
    RepositoryReleaseAuditLedgerVerificationResponse,
)

router = APIRouter()


def serialize_release_audit_ledger_entry(
    entry: RepositoryReleaseAuditLedgerEntry,
) -> RepositoryReleaseAuditLedgerEntryResponse:
    return RepositoryReleaseAuditLedgerEntryResponse(
        sequence=entry.sequence,
        bundle_id=entry.bundle_id,
        repository_name=entry.repository_name,
        accepted=entry.accepted,
        previous_entry_hash=entry.previous_entry_hash,
        entry_hash=entry.entry_hash,
    )


def serialize_release_audit_ledger(
    ledger: RepositoryReleaseAuditLedger,
) -> RepositoryReleaseAuditLedgerResponse:
    verification = RepositoryReleaseAuditLedgerVerifier().verify(
        ledger
    )
    summary = RepositoryReleaseAuditLedgerSummaryBuilder().build(
        ledger,
        verification,
    )

    return RepositoryReleaseAuditLedgerResponse(
        schema_version=ledger.schema_version,
        ledger_id=ledger.ledger_id,
        ledger_valid=verification.valid,
        status=ledger.status,
        entries=[
            serialize_release_audit_ledger_entry(entry)
            for entry in ledger.entries
        ],
        entry_count=ledger.entry_count,
        accepted_entry_count=ledger.accepted_entry_count,
        rejected_entry_count=ledger.rejected_entry_count,
        repository_names=ledger.repository_names,
        latest_entry_hash=ledger.latest_entry_hash,
        all_entries_accepted=ledger.all_entries_accepted,
        ledger_json=ledger.as_json(),
        ledger_markdown=ledger.as_markdown(),
        verification=(
            RepositoryReleaseAuditLedgerVerificationResponse(
                integrity_valid=verification.integrity_valid,
                chain_valid=verification.chain_valid,
                valid=verification.valid,
                invalid_entry_sequences=(
                    verification.invalid_entry_sequences
                ),
            )
        ),
        summary=RepositoryReleaseAuditLedgerSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-release-audit-ledger",
    response_model=RepositoryReleaseAuditLedgerResponse,
    status_code=status.HTTP_200_OK,
)
def create_repository_release_audit_ledger(
    data: RepositoryReleaseAuditLedgerRequest,
):
    try:
        ledger = RepositoryReleaseAuditLedgerBuilder().build(
            bundle_json_values=data.bundle_json_values,
            require_accepted=data.require_accepted,
        )

        return serialize_release_audit_ledger(ledger)

    except (
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
