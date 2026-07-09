from pydantic import BaseModel


class RepositoryReadinessCheckResponse(BaseModel):
    name: str
    passed: bool
    message: str


class RepositoryReadinessReportResponse(BaseModel):
    checks: list[RepositoryReadinessCheckResponse]
    passed: bool
    passed_count: int
    failed_count: int


class RepositoryObjectiveCloseoutResponse(BaseModel):
    objective_name: str
    status: str
    can_close: bool
    readiness: RepositoryReadinessReportResponse
    next_action: str
