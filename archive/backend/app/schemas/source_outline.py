from pydantic import BaseModel, Field


class SourceOutlinePreviewRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)


class SourceOutlineSymbolResponse(BaseModel):
    name: str
    symbol_type: str
    line_number: int


class SourceOutlineFileResponse(BaseModel):
    path: str
    suffix: str
    language: str
    symbols: list[SourceOutlineSymbolResponse]
    symbol_count: int
    function_count: int
    class_count: int


class SourceOutlineOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class SourceOutlinePreviewResponse(BaseModel):
    file_count: int
    symbol_count: int
    function_count: int
    class_count: int
    files_with_symbols_count: int
    files: list[SourceOutlineFileResponse]
    summary: SourceOutlineOperatorSummaryResponse
