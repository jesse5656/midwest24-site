from pydantic import BaseModel, Field


class GitCommitPreviewRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)


class GitCommitResponse(BaseModel):
    sha: str
    short_sha: str
    author_name: str
    author_email: str
    authored_at: str
    subject: str
    display: str


class GitAuthorContributionResponse(BaseModel):
    author_name: str
    author_email: str
    commit_count: int


class GitCommitPreviewOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class GitCommitPreviewResponse(BaseModel):
    commit_count: int
    commits: list[GitCommitResponse]
    authors: list[GitAuthorContributionResponse]
    latest_commit: GitCommitResponse | None
    oldest_commit: GitCommitResponse | None
    summary: GitCommitPreviewOperatorSummaryResponse
