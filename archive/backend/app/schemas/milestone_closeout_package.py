from pydantic import BaseModel, Field


class MilestoneCloseoutPackageRequest(BaseModel):
    test_count: int = Field(..., ge=0)


class MilestoneCloseoutItemResponse(BaseModel):
    name: str
    completed: bool
    evidence: str


class MilestoneCloseoutSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class MilestoneCloseoutPackageResponse(BaseModel):
    milestone_name: str
    test_count: int
    items: list[MilestoneCloseoutItemResponse]
    item_count: int
    completed_count: int
    incomplete_count: int
    is_complete: bool
    completion_ratio: float
    summary: MilestoneCloseoutSummaryResponse
