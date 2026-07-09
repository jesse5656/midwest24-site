from pydantic import BaseModel, Field


class GitRepositoryIntelligenceRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    commit_limit: int = Field(default=5, ge=1, le=50)


class GitRepositoryIntelligenceResponse(BaseModel):
    is_repository: bool
    root: str | None
    current_branch: str | None
    recent_commit_count: int
    is_clean: bool | None


class GitRepositoryOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class GitRepositoryIntelligenceEnvelopeResponse(BaseModel):
    intelligence: GitRepositoryIntelligenceResponse
    summary: GitRepositoryOperatorSummaryResponse
