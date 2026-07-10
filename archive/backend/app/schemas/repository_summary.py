from pydantic import BaseModel, Field


class RepositorySummaryRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositorySummarySectionResponse(BaseModel):
    name: str
    value: str


class RepositorySummarySummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositorySummaryResponse(BaseModel):
    repository_path: str
    title: str
    sections: list[RepositorySummarySectionResponse]
    section_count: int
    section_names: list[str]
    summary: RepositorySummarySummaryResponse
