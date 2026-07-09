from pydantic import BaseModel


class OperatorExecutionChecklistItemResponse(BaseModel):
    name: str
    completed: bool
    evidence: str


class OperatorExecutionChecklistSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class OperatorExecutionChecklistResponse(BaseModel):
    name: str
    items: list[OperatorExecutionChecklistItemResponse]
    item_count: int
    completed_count: int
    incomplete_count: int
    is_complete: bool
    summary: OperatorExecutionChecklistSummaryResponse
