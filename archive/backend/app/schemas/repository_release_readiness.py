from pydantic import BaseModel, Field

from app.schemas.repository_snapshot_policy import (
    RepositorySnapshotPolicyData,
)


class RepositoryReleaseReadinessRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    baseline_json: str = Field(..., min_length=2)
    policy: RepositorySnapshotPolicyData = Field(
        default_factory=RepositorySnapshotPolicyData
    )
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryReleaseReadinessCheckResponse(BaseModel):
    name: str
    passed: bool
    severity: str
    message: str


class RepositoryReleaseReadinessSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseReadinessResponse(BaseModel):
    repository_path: str
    repository_name: str
    release_ready: bool
    blocked: bool
    status: str
    exit_code: int
    checks: list[RepositoryReleaseReadinessCheckResponse]
    check_count: int
    passed_check_count: int
    failed_check_count: int
    critical_failure_count: int
    warning_failure_count: int
    failed_check_names: list[str]
    gate_passed: bool
    gate_reason_count: int
    dashboard_healthy: bool
    dashboard_warning_count: int
    summary: RepositoryReleaseReadinessSummaryResponse
