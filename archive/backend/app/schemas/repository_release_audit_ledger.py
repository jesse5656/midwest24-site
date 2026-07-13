from pydantic import BaseModel, Field


class RepositoryReleaseAuditLedgerRequest(BaseModel):
    bundle_json_values: list[str] = Field(
        ...,
        min_length=1,
    )
    require_accepted: bool = False


class RepositoryReleaseAuditLedgerEntryResponse(BaseModel):
    sequence: int
    bundle_id: str
    repository_name: str
    accepted: bool
    previous_entry_hash: str
    entry_hash: str


class RepositoryReleaseAuditLedgerVerificationResponse(
    BaseModel
):
    integrity_valid: bool
    chain_valid: bool
    valid: bool
    invalid_entry_sequences: list[int]


class RepositoryReleaseAuditLedgerSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerResponse(BaseModel):
    schema_version: str
    ledger_id: str
    ledger_valid: bool
    status: str
    entries: list[
        RepositoryReleaseAuditLedgerEntryResponse
    ]
    entry_count: int
    accepted_entry_count: int
    rejected_entry_count: int
    repository_names: list[str]
    latest_entry_hash: str
    all_entries_accepted: bool
    ledger_json: str
    ledger_markdown: str
    verification: RepositoryReleaseAuditLedgerVerificationResponse
    summary: RepositoryReleaseAuditLedgerSummaryResponse
