from pydantic import BaseModel, Field


class CodeObjectiveScorecardRequest(BaseModel):
    test_count: int = Field(..., ge=0)


class CodeObjectiveCapabilityResponse(BaseModel):
    name: str
    completed: bool
    evidence: str


class CodeObjectiveOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class CodeObjectiveScorecardResponse(BaseModel):
    objective_name: str
    capabilities: list[CodeObjectiveCapabilityResponse]
    test_count: int
    capability_count: int
    completed_capability_count: int
    incomplete_capability_count: int
    completion_ratio: float
    is_complete: bool
    summary: CodeObjectiveOperatorSummaryResponse
