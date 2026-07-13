from pydantic import BaseModel, Field


class RepositoryIntelligenceDashboardRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryIntelligenceMetricResponse(BaseModel):
    name: str
    value: int
    status: str
    description: str


class RepositoryIntelligenceDashboardSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryIntelligenceDashboardResponse(BaseModel):
    repository_path: str
    repository_name: str
    metrics: list[RepositoryIntelligenceMetricResponse]
    warnings: list[str]
    metric_count: int
    warning_count: int
    healthy_metric_count: int
    warning_metric_count: int
    critical_metric_count: int
    is_healthy: bool
    metric_names: list[str]
    summary: RepositoryIntelligenceDashboardSummaryResponse
