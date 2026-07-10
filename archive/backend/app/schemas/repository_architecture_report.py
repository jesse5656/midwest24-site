from pydantic import BaseModel, Field


class RepositoryArchitectureReportRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryArchitectureFindingResponse(BaseModel):
    name: str
    severity: str
    message: str


class RepositoryArchitectureReportSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryArchitectureReportResponse(BaseModel):
    repository_path: str
    title: str
    findings: list[RepositoryArchitectureFindingResponse]
    finding_count: int
    severity_levels: list[str]
    info_count: int
    warning_count: int
    critical_count: int
    has_warnings: bool
    summary: RepositoryArchitectureReportSummaryResponse
