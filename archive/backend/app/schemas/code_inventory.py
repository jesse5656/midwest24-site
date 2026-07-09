from pydantic import BaseModel, Field


class CodeInventoryPreviewRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)


class CodeInventoryFileResponse(BaseModel):
    path: str
    suffix: str
    language: str
    size_bytes: int


class CodeInventoryLanguageSummaryResponse(BaseModel):
    language: str
    file_count: int
    size_bytes: int


class CodeInventoryOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class CodeInventoryPreviewResponse(BaseModel):
    file_count: int
    total_size_bytes: int
    language_count: int
    languages: list[str]
    largest_file: CodeInventoryFileResponse | None
    language_summaries: list[CodeInventoryLanguageSummaryResponse]
    files: list[CodeInventoryFileResponse]
    summary: CodeInventoryOperatorSummaryResponse
