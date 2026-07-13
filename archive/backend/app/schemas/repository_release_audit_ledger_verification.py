from pydantic import BaseModel, Field


class RepositoryReleaseAuditLedgerVerificationRequest(
    BaseModel
):
    ledger_json: str = Field(..., min_length=2)
    require_all_accepted: bool = True
    expected_ledger_id: str | None = None
    expected_bundle_ids: list[str] | None = None


class RepositoryReleaseAuditLedgerVerificationIssueResponse(
    BaseModel
):
    code: str
    severity: str
    message: str
    sequence: int | None = None


class RepositoryReleaseAuditLedgerVerificationSummaryResponse(
    BaseModel
):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerVerificationResponse(
    BaseModel
):
    ledger_id: str
    schema_version: str
    integrity_valid: bool
    chain_valid: bool
    valid: bool
    accepted: bool
    rejected: bool
    status: str
    entry_count: int
    accepted_entry_count: int
    rejected_entry_count: int
    issues: list[
        RepositoryReleaseAuditLedgerVerificationIssueResponse
    ]
    issue_count: int
    critical_issue_count: int
    error_issue_count: int
    warning_issue_count: int
    issue_codes: list[str]
    invalid_entry_sequences: list[int]
    summary: (
        RepositoryReleaseAuditLedgerVerificationSummaryResponse
    )
