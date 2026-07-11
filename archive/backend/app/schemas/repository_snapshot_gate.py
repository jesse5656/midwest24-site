from pydantic import BaseModel, Field

from app.schemas.repository_snapshot_policy import (
    RepositorySnapshotPolicyData,
)


class RepositorySnapshotGateRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    baseline_json: str = Field(..., min_length=2)
    policy: RepositorySnapshotPolicyData = Field(
        default_factory=RepositorySnapshotPolicyData
    )
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositorySnapshotGateReasonResponse(BaseModel):
    code: str
    message: str
    severity: str


class RepositorySnapshotGateSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositorySnapshotGateResponse(BaseModel):
    repository_path: str
    passed: bool
    blocked: bool
    status: str
    exit_code: int
    reason_count: int
    critical_reason_count: int
    warning_reason_count: int
    reason_codes: list[str]
    reasons: list[RepositorySnapshotGateReasonResponse]
    baseline_matches: bool
    baseline_fingerprint_matches: bool
    baseline_difference_count: int
    policy_passed: bool
    policy_violation_count: int
    summary: RepositorySnapshotGateSummaryResponse
