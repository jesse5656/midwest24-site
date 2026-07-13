from pydantic import BaseModel, Field


class RepositoryReleaseAuditLedgerProgressionGateRequest(
    BaseModel
):
    baseline_snapshot_json: str = Field(
        ...,
        min_length=2,
    )
    candidate_snapshot_json: str = Field(
        ...,
        min_length=2,
    )
    allow_unchanged: bool = True
    require_candidate_accepted: bool = True


class RepositoryReleaseAuditLedgerProgressionGateReasonResponse(
    BaseModel
):
    code: str
    severity: str
    message: str


class RepositoryReleaseAuditLedgerProgressionGateSummaryResponse(
    BaseModel
):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerProgressionGateResponse(
    BaseModel
):
    baseline_snapshot_id: str
    candidate_snapshot_id: str
    baseline_valid: bool
    candidate_valid: bool
    baseline_accepted: bool
    candidate_accepted: bool
    snapshots_identical: bool
    append_only: bool
    history_rewritten: bool
    acceptance_regression: bool
    safe_progression: bool
    entry_count_delta: int
    added_bundle_ids: list[str]
    removed_bundle_ids: list[str]
    allow_unchanged: bool
    require_candidate_accepted: bool
    passed: bool
    blocked: bool
    exit_code: int
    status: str
    reasons: list[
        RepositoryReleaseAuditLedgerProgressionGateReasonResponse
    ]
    reason_count: int
    critical_reason_count: int
    error_reason_count: int
    warning_reason_count: int
    reason_codes: list[str]
    summary: (
        RepositoryReleaseAuditLedgerProgressionGateSummaryResponse
    )
