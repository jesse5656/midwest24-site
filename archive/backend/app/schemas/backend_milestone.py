from pydantic import BaseModel, Field


class BackendMilestoneScorecardRequest(BaseModel):
    test_count: int = Field(..., ge=0)


class BackendMilestoneCapabilityResponse(BaseModel):
    name: str
    completed: bool
    evidence: str


class BackendMilestoneOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class BackendMilestoneReadinessCheckResponse(BaseModel):
    name: str
    passed: bool
    message: str


class BackendMilestoneReadinessReportResponse(BaseModel):
    checks: list[BackendMilestoneReadinessCheckResponse]
    passed: bool
    passed_count: int
    failed_count: int


class BackendMilestoneCloseoutResponse(BaseModel):
    milestone_name: str
    status: str
    can_close: bool
    readiness: BackendMilestoneReadinessReportResponse
    next_action: str


class BackendMilestoneScorecardResponse(BaseModel):
    milestone_name: str
    test_count: int
    capabilities: list[BackendMilestoneCapabilityResponse]
    capability_count: int
    completed_capability_count: int
    incomplete_capability_count: int
    completion_ratio: float
    is_complete: bool
    summary: BackendMilestoneOperatorSummaryResponse
    closeout: BackendMilestoneCloseoutResponse
