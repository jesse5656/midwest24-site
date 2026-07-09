from pydantic import BaseModel, Field


class GitFileChangePreviewRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)


class GitFileChangeResponse(BaseModel):
    status: str
    path: str
    is_added: bool
    is_modified: bool
    is_deleted: bool
    is_renamed: bool


class GitCommitFileChangeSetResponse(BaseModel):
    commit_sha: str
    short_sha: str
    subject: str
    files: list[GitFileChangeResponse]
    file_count: int
    added_count: int
    modified_count: int
    deleted_count: int
    renamed_count: int


class GitFileChangeOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class GitFileChangePreviewResponse(BaseModel):
    commit_count: int
    file_change_count: int
    added_count: int
    modified_count: int
    deleted_count: int
    renamed_count: int
    touched_paths: list[str]
    commits: list[GitCommitFileChangeSetResponse]
    summary: GitFileChangeOperatorSummaryResponse
