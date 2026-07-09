from pydantic import BaseModel, Field


class GitAuthorshipPreviewRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    limit: int = Field(default=50, ge=1, le=250)


class GitAuthorSummaryResponse(BaseModel):
    author_name: str
    author_email: str
    commit_count: int
    first_authored_at: str
    last_authored_at: str
    identity: str


class GitAuthorshipOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class GitAuthorshipPreviewResponse(BaseModel):
    commit_count: int
    author_count: int
    authors: list[GitAuthorSummaryResponse]
    top_author: GitAuthorSummaryResponse | None
    first_authored_at: str | None
    last_authored_at: str | None
    summary: GitAuthorshipOperatorSummaryResponse
