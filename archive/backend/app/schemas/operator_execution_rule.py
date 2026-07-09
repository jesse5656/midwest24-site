from pydantic import BaseModel, Field


class OperatorExecutionRuleRequest(BaseModel):
    test_count: int = Field(..., ge=0)
    target_test_count: int = Field(..., ge=0)


class OperatorExecutionRuleResponse(BaseModel):
    name: str
    instruction: str
    rationale: str
    required: bool


class OperatorExecutionRuleSetResponse(BaseModel):
    rules: list[OperatorExecutionRuleResponse]
    rule_count: int
    required_count: int
    optional_count: int
    is_complete: bool


class OperatorExecutionPromptResponse(BaseModel):
    test_count: int
    target_test_count: int
    delta: int
    is_forward_progress: bool
    rendered_prompt: str
    rule: OperatorExecutionRuleResponse


class OperatorExecutionSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class OperatorExecutionEnvelopeResponse(BaseModel):
    ruleset: OperatorExecutionRuleSetResponse
    prompt: OperatorExecutionPromptResponse
    ruleset_summary: OperatorExecutionSummaryResponse
    prompt_summary: OperatorExecutionSummaryResponse
