from pydantic import BaseModel, Field


class RepositorySearchIndexRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)
    query: str = ""
    limit: int = Field(default=10, ge=1, le=50)


class RepositorySearchDocumentResponse(BaseModel):
    document_id: str
    document_type: str
    title: str
    body: str
    source: str


class RepositorySearchResultResponse(BaseModel):
    document_id: str
    document_type: str
    title: str
    source: str
    score: int


class RepositorySearchIndexSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositorySearchIndexResponse(BaseModel):
    repository_path: str
    documents: list[RepositorySearchDocumentResponse]
    document_count: int
    document_types: list[str]
    results: list[RepositorySearchResultResponse]
    result_count: int
    summary: RepositorySearchIndexSummaryResponse
