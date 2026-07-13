from pydantic import BaseModel, Field


class RepositorySnapshotComparisonRequest(BaseModel):
    baseline_repository_path: str = Field(
        ...,
        min_length=1,
    )
    candidate_repository_path: str = Field(
        ...,
        min_length=1,
    )
    max_depth: int = Field(
        default=8,
        ge=1,
        le=30,
    )


class RepositorySnapshotMetricChangeResponse(BaseModel):
    name: str
    baseline_value: int | None
    candidate_value: int | None
    delta: int | None
    change_type: str


class RepositorySnapshotComparisonSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositorySnapshotComparisonResponse(BaseModel):
    baseline_repository_path: str
    candidate_repository_path: str
    baseline_fingerprint: str
    candidate_fingerprint: str
    fingerprints_match: bool
    has_changes: bool
    metric_changes: list[
        RepositorySnapshotMetricChangeResponse
    ]
    metric_change_count: int
    increased_metric_count: int
    decreased_metric_count: int
    added_metric_count: int
    removed_metric_count: int
    unchanged_metric_count: int
    changed_metric_names: list[str]
    node_delta: int
    edge_delta: int
    report_section_delta: int
    warning_delta: int
    critical_delta: int
    summary: RepositorySnapshotComparisonSummaryResponse
