from pydantic import BaseModel, Field


class GitObjectiveScorecardRequest(BaseModel):
    test_count: int = Field(..., ge=0)


class GitObjectiveCapabilityResponse(BaseModel):
    name: str
    completed: bool
    evidence: str


class GitObjectiveOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class GitObjectiveScorecardResponse(BaseModel):
    objective_name: str
    capabilities: list[GitObjectiveCapabilityResponse]
    test_count: int
    capability_count: int
    completed_capability_count: int
    incomplete_capability_count: int
    completion_ratio: float
    is_complete: bool
    summary: GitObjectiveOperatorSummaryResponse
