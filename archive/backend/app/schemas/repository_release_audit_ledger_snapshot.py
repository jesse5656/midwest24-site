from pydantic import BaseModel, Field


class RepositoryReleaseAuditLedgerSnapshotRequest(
    BaseModel
):
    ledger_json: str = Field(..., min_length=2)
    require_all_accepted: bool = True


class RepositoryReleaseAuditLedgerSnapshotEntryResponse(
    BaseModel
):
    sequence: int
    bundle_id: str
    repository_name: str
    accepted: bool
    entry_hash: str


class RepositoryReleaseAuditLedgerSnapshotSummaryResponse(
    BaseModel
):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerSnapshotResponse(
    BaseModel
):
    schema_version: str
    snapshot_id: str
    snapshot_valid: bool
    ledger_id: str
    ledger_integrity_valid: bool
    ledger_chain_valid: bool
    ledger_accepted: bool
    accepted: bool
    rejected: bool
    status: str
    entry_count: int
    accepted_entry_count: int
    rejected_entry_count: int
    latest_entry_hash: str
    repository_names: list[str]
    repository_count: int
    entries: list[
        RepositoryReleaseAuditLedgerSnapshotEntryResponse
    ]
    issue_codes: list[str]
    issue_count: int
    snapshot_json: str
    snapshot_markdown: str
    summary: (
        RepositoryReleaseAuditLedgerSnapshotSummaryResponse
    )
