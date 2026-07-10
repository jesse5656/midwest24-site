from pydantic import BaseModel, Field


class RepositoryDriftDetectionRequest(BaseModel):
    baseline_repository_path: str = Field(..., min_length=1)
    candidate_repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryDriftFindingResponse(BaseModel):
    finding_type: str
    severity: str
    subject: str
    message: str


class RepositoryDriftSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryDriftDetectionResponse(BaseModel):
    baseline_repository_path: str
    candidate_repository_path: str
    findings: list[RepositoryDriftFindingResponse]
    finding_count: int
    has_drift: bool
    added_count: int
    removed_count: int
    warning_count: int
    critical_count: int
    finding_types: list[str]
    severity_levels: list[str]
    summary: RepositoryDriftSummaryResponse
