from pydantic import BaseModel, Field


class RepositorySemanticSearchRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)
    limit: int = Field(default=10, ge=1, le=50)


class RepositorySemanticSearchResultResponse(BaseModel):
    document_id: str
    document_type: str
    title: str
    source: str
    lexical_score: int
    concept_score: int
    total_score: int
    matched_terms: list[str]


class RepositorySemanticSearchSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositorySemanticSearchResponse(BaseModel):
    repository_path: str
    query: str
    results: list[RepositorySemanticSearchResultResponse]
    result_count: int
    document_types: list[str]
    highest_score: int
    summary: RepositorySemanticSearchSummaryResponse
