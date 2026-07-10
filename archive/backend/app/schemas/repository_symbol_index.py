from pydantic import BaseModel, Field


class RepositorySymbolIndexRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositorySymbolResponse(BaseModel):
    name: str
    symbol_type: str
    source_file: str
    line_number: int
    parent: str | None
    qualified_name: str


class RepositorySymbolIndexSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositorySymbolIndexResponse(BaseModel):
    repository_path: str
    symbols: list[RepositorySymbolResponse]
    symbol_count: int
    source_file_count: int
    source_files: list[str]
    symbol_types: list[str]
    class_count: int
    function_count: int
    method_count: int
    constant_count: int
    summary: RepositorySymbolIndexSummaryResponse
