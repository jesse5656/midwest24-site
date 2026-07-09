from pydantic import BaseModel, Field


class GitBranchAnalysisRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)


class GitBranchResponse(BaseModel):
    name: str
    current: bool


class GitBranchAnalysisOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class GitBranchAnalysisResponse(BaseModel):
    branch_count: int
    branches: list[GitBranchResponse]
    current_branch: GitBranchResponse | None
    current_branch_name: str | None
    has_multiple_branches: bool
    branch_names: list[str]
    non_current_branch_names: list[str]
    summary: GitBranchAnalysisOperatorSummaryResponse
