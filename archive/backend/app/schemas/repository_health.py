from pydantic import BaseModel, Field


class ArchiveBackendHealthRequest(BaseModel):
    test_count: int = Field(..., ge=0)
    has_progress_ledger: bool = True
    has_operating_plan: bool = True
    has_runbook: bool = True
    has_git_intelligence: bool = True
    has_code_intelligence: bool = True


class RepositoryHealthCheckResponse(BaseModel):
    name: str
    passed: bool
    message: str
    severity: str


class RepositoryHealthOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryHealthReportResponse(BaseModel):
    name: str
    checks: list[RepositoryHealthCheckResponse]
    passed: bool
    check_count: int
    passed_count: int
    failed_count: int
    warning_count: int
    error_count: int
    summary: RepositoryHealthOperatorSummaryResponse
