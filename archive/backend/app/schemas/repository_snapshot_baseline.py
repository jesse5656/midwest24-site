from pydantic import BaseModel, Field


class RepositorySnapshotBaselineCreateRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositorySnapshotBaselineMetricResponse(BaseModel):
    name: str
    value: int
    status: str


class RepositorySnapshotBaselineData(BaseModel):
    schema_version: str
    repository_name: str
    fingerprint: str
    metrics: list[RepositorySnapshotBaselineMetricResponse]
    node_count: int
    edge_count: int
    report_section_count: int
    warning_count: int
    critical_count: int


class RepositorySnapshotBaselineSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositorySnapshotBaselineCreateResponse(BaseModel):
    baseline: RepositorySnapshotBaselineData
    metric_count: int
    metric_names: list[str]
    is_healthy: bool
    baseline_json: str
    checksum: str
    summary: RepositorySnapshotBaselineSummaryResponse


class RepositorySnapshotBaselineVerifyRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    baseline_json: str = Field(..., min_length=2)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositorySnapshotBaselineVerifyResponse(BaseModel):
    matches: bool
    fingerprint_matches: bool
    difference_count: int
    metric_differences: list[str]
    baseline_fingerprint: str
    candidate_fingerprint: str
    summary: RepositorySnapshotBaselineSummaryResponse
