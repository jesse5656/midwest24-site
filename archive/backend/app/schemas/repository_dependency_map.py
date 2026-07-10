from pydantic import BaseModel, Field


class RepositoryDependencyMapRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=5, ge=1, le=20)


class RepositoryDependencyResponse(BaseModel):
    name: str
    source_file: str
    ecosystem: str
    dependency_type: str


class RepositoryDependencyMapSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryDependencyMapResponse(BaseModel):
    repository_path: str
    dependencies: list[RepositoryDependencyResponse]
    dependency_count: int
    ecosystem_count: int
    ecosystems: list[str]
    runtime_count: int
    development_count: int
    summary: RepositoryDependencyMapSummaryResponse
