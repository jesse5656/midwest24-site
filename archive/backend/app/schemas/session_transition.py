from pydantic import BaseModel, Field


class SessionTransitionRequest(BaseModel):
    test_count: int = Field(..., ge=0)


class SessionTransitionCommandSetResponse(BaseModel):
    repository_path: str
    commands: list[str]


class SessionTransitionOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class SessionTransitionPromptResponse(BaseModel):
    repository_path: str
    source_of_truth: str
    current_objective: str
    completed: list[str]
    next_steps: list[str]
    deferred: list[str]
    completed_count: int
    next_step_count: int
    deferred_count: int
    command_set: SessionTransitionCommandSetResponse
    rendered_prompt: str
    summary: SessionTransitionOperatorSummaryResponse
