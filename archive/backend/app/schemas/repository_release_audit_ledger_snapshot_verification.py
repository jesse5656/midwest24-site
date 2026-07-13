from pydantic import BaseModel, Field


class RepositoryReleaseAuditLedgerSnapshotVerificationRequest(
    BaseModel
):
    snapshot_json: str = Field(..., min_length=2)
    require_accepted: bool = True
    expected_snapshot_id: str | None = None
    expected_ledger_id: str | None = None
    expected_latest_entry_hash: str | None = None
    expected_bundle_ids: list[str] | None = None


class RepositoryReleaseAuditLedgerSnapshotVerificationIssueResponse(
    BaseModel
):
    code: str
    severity: str
    message: str
    sequence: int | None = None


class RepositoryReleaseAuditLedgerSnapshotVerificationSummaryResponse(
    BaseModel
):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerSnapshotVerificationResponse(
    BaseModel
):
    snapshot_id: str
    ledger_id: str
    schema_version: str
    snapshot_accepted: bool
    integrity_valid: bool
    valid: bool
    accepted: bool
    rejected: bool
    status: str
    entry_count: int
    accepted_entry_count: int
    rejected_entry_count: int
    repository_count: int
    issues: list[
        RepositoryReleaseAuditLedgerSnapshotVerificationIssueResponse
    ]
    issue_count: int
    critical_issue_count: int
    error_issue_count: int
    warning_issue_count: int
    issue_codes: list[str]
    invalid_entry_sequences: list[int]
    summary: (
        RepositoryReleaseAuditLedgerSnapshotVerificationSummaryResponse
    )
