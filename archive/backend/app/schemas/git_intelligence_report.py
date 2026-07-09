from pydantic import BaseModel, Field

from app.schemas.git_authorship_preview import GitAuthorshipPreviewResponse
from app.schemas.git_commit_preview import GitCommitPreviewResponse
from app.schemas.git_file_change_preview import GitFileChangePreviewResponse
from app.schemas.git_repository_intelligence import GitRepositoryIntelligenceResponse


class GitIntelligenceReportRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    limit: int = Field(default=25, ge=1, le=100)


class GitIntelligenceOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class GitIntelligenceReadinessCheckResponse(BaseModel):
    name: str
    passed: bool
    message: str


class GitIntelligenceReadinessReportResponse(BaseModel):
    checks: list[GitIntelligenceReadinessCheckResponse]
    passed: bool
    passed_count: int
    failed_count: int


class GitIntelligenceCloseoutResponse(BaseModel):
    objective_name: str
    status: str
    can_close: bool
    readiness: GitIntelligenceReadinessReportResponse
    next_action: str


class GitIntelligenceReportResponse(BaseModel):
    repository: GitRepositoryIntelligenceResponse
    commits: GitCommitPreviewResponse
    file_changes: GitFileChangePreviewResponse
    authorship: GitAuthorshipPreviewResponse
    is_repository: bool
    current_branch: str | None
    commit_count: int
    file_change_count: int
    author_count: int
    has_uncommitted_changes: bool
    is_ready: bool
    summary: GitIntelligenceOperatorSummaryResponse
    closeout: GitIntelligenceCloseoutResponse
