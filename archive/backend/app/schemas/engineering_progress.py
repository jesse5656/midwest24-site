from pydantic import BaseModel, Field


class EngineeringProgressRequest(BaseModel):
    test_count: int = Field(default=3208, ge=0)


class EngineeringCapabilityResponse(BaseModel):
    name: str
    status: str
    evidence: str
    is_complete: bool
    is_in_progress: bool
    is_remaining: bool


class EngineeringProgressSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class EngineeringProgressResponse(BaseModel):
    milestone_name: str
    test_count: int
    capability_count: int
    complete_count: int
    in_progress_count: int
    remaining_count: int
    percent_complete: float
    capabilities: list[EngineeringCapabilityResponse]
    completed_capabilities: list[EngineeringCapabilityResponse]
    in_progress_capabilities: list[EngineeringCapabilityResponse]
    remaining_capabilities: list[EngineeringCapabilityResponse]
    summary: EngineeringProgressSummaryResponse
