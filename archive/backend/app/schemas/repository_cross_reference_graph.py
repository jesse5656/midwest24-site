from pydantic import BaseModel, Field


class RepositoryCrossReferenceGraphRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryCrossReferenceResponse(BaseModel):
    source_file: str
    source_symbol: str | None
    referenced_name: str
    reference_type: str
    line_number: int


class RepositoryCrossReferenceGraphSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryCrossReferenceGraphResponse(BaseModel):
    repository_path: str
    references: list[RepositoryCrossReferenceResponse]
    reference_count: int
    source_file_count: int
    referenced_name_count: int
    source_files: list[str]
    referenced_names: list[str]
    call_count: int
    attribute_count: int
    name_count: int
    summary: RepositoryCrossReferenceGraphSummaryResponse
