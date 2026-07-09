from pydantic import BaseModel, Field


class OperatorSessionGuardRequest(BaseModel):
    current_test_count: int = Field(..., ge=0)
    target_test_count: int = Field(..., ge=0)
    uses_python_file_writers: bool = True
    avoids_nested_heredocs: bool = True
    includes_test_run: bool = True
    separates_commit_commands: bool = True


class OperatorSessionGuardRuleResponse(BaseModel):
    name: str
    passed: bool
    message: str


class OperatorSessionGuardSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class OperatorSessionGuardReportResponse(BaseModel):
    current_test_count: int
    target_test_count: int
    delta: int
    is_forward_progress: bool
    rule_count: int
    passed_count: int
    failed_count: int
    passed: bool
    rules: list[OperatorSessionGuardRuleResponse]
    failed_rules: list[OperatorSessionGuardRuleResponse]
    summary: OperatorSessionGuardSummaryResponse
