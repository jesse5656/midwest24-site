from pydantic import BaseModel, Field

from app.schemas.code_inventory import CodeInventoryPreviewResponse
from app.schemas.source_outline import SourceOutlinePreviewResponse


class CodeIntelligenceReportRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)


class CodeIntelligenceOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class CodeIntelligenceReadinessCheckResponse(BaseModel):
    name: str
    passed: bool
    message: str


class CodeIntelligenceReadinessReportResponse(BaseModel):
    checks: list[CodeIntelligenceReadinessCheckResponse]
    passed: bool
    passed_count: int
    failed_count: int


class CodeIntelligenceCloseoutResponse(BaseModel):
    objective_name: str
    status: str
    can_close: bool
    readiness: CodeIntelligenceReadinessReportResponse
    next_action: str


class CodeIntelligenceReportResponse(BaseModel):
    inventory: CodeInventoryPreviewResponse
    outline: SourceOutlinePreviewResponse
    file_count: int
    language_count: int
    symbol_count: int
    function_count: int
    class_count: int
    files_with_symbols_count: int
    has_inventory: bool
    has_outline: bool
    is_ready: bool
    summary: CodeIntelligenceOperatorSummaryResponse
    closeout: CodeIntelligenceCloseoutResponse
