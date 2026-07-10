from pydantic import BaseModel, Field


class RepositorySnapshotPolicyData(BaseModel):
    require_fingerprint_match: bool = False
    allow_added_metrics: bool = True
    allow_removed_metrics: bool = False
    max_warning_delta: int = Field(default=0, ge=0)
    max_critical_delta: int = Field(default=0, ge=0)
    max_node_decrease: int = Field(default=0, ge=0)
    max_edge_decrease: int = Field(default=0, ge=0)
    max_metric_decrease: int = Field(default=0, ge=0)


class RepositorySnapshotPolicyRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    baseline_json: str = Field(..., min_length=2)
    policy: RepositorySnapshotPolicyData = Field(
        default_factory=RepositorySnapshotPolicyData
    )
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositorySnapshotPolicyViolationResponse(BaseModel):
    rule: str
    subject: str
    message: str
    severity: str


class RepositorySnapshotPolicySummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositorySnapshotPolicyResponse(BaseModel):
    repository_path: str
    baseline_fingerprint: str
    candidate_fingerprint: str
    passed: bool
    violation_count: int
    failed_rules: list[str]
    critical_violation_count: int
    error_violation_count: int
    violations: list[
        RepositorySnapshotPolicyViolationResponse
    ]
    summary: RepositorySnapshotPolicySummaryResponse
