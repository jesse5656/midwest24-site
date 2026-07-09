from pydantic import BaseModel, Field


class OperatorProgressTargetRequest(BaseModel):
    current_test_count: int = Field(..., ge=0)
    target_test_count: int = Field(..., ge=0)


class OperatorProgressTargetResponse(BaseModel):
    current_test_count: int
    target_test_count: int
    delta: int
    is_valid: bool
    percent_complete: float
    remaining_tests: int


class OperatorProgressMilestoneResponse(BaseModel):
    name: str
    test_count: int
    reached: bool


class OperatorProgressSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class OperatorProgressPlanResponse(BaseModel):
    target: OperatorProgressTargetResponse
    milestones: list[OperatorProgressMilestoneResponse]
    milestone_count: int
    reached_count: int
    unreached_count: int
    next_milestone: OperatorProgressMilestoneResponse | None
    summary: OperatorProgressSummaryResponse
