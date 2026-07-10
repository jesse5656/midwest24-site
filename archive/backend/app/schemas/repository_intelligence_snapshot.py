from pydantic import BaseModel, Field


class RepositoryIntelligenceSnapshotRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryIntelligenceSnapshotMetricResponse(BaseModel):
    name: str
    value: int
    status: str


class RepositoryIntelligenceSnapshotSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryIntelligenceSnapshotResponse(BaseModel):
    repository_path: str
    repository_name: str
    metrics: list[
        RepositoryIntelligenceSnapshotMetricResponse
    ]
    metric_count: int
    metric_names: list[str]
    node_count: int
    edge_count: int
    report_section_count: int
    warning_count: int
    critical_count: int
    is_healthy: bool
    fingerprint: str
    canonical_json: str
    summary: RepositoryIntelligenceSnapshotSummaryResponse
