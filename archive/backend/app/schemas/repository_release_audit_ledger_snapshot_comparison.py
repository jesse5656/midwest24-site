from pydantic import BaseModel, Field


class RepositoryReleaseAuditLedgerSnapshotComparisonRequest(
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
    require_accepted: bool = False


class RepositoryReleaseAuditLedgerSnapshotComparisonSummaryResponse(
    BaseModel
):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerSnapshotComparisonResponse(
    BaseModel
):
    baseline_snapshot_id: str
    candidate_snapshot_id: str
    baseline_ledger_id: str
    candidate_ledger_id: str
    baseline_valid: bool
    candidate_valid: bool
    baseline_accepted: bool
    candidate_accepted: bool
    baseline_entry_count: int
    candidate_entry_count: int
    entry_count_delta: int
    added_bundle_ids: list[str]
    removed_bundle_ids: list[str]
    append_only: bool
    history_rewritten: bool
    acceptance_regression: bool
    acceptance_improvement: bool
    ledger_changed: bool
    snapshots_identical: bool
    changed: bool
    safe_progression: bool
    status: str
    summary: (
        RepositoryReleaseAuditLedgerSnapshotComparisonSummaryResponse
    )
