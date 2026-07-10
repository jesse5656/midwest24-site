from pydantic import BaseModel, Field


class RepositoryImportGraphRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryImportEdgeResponse(BaseModel):
    source_file: str
    imported_name: str
    import_type: str
    line_number: int


class RepositoryImportGraphSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryImportGraphResponse(BaseModel):
    repository_path: str
    edges: list[RepositoryImportEdgeResponse]
    edge_count: int
    source_file_count: int
    imported_name_count: int
    source_files: list[str]
    imported_names: list[str]
    summary: RepositoryImportGraphSummaryResponse
