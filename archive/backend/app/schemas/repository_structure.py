from pydantic import BaseModel, Field


class RepositoryStructureRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=4, ge=1, le=20)


class RepositoryStructureNodeResponse(BaseModel):
    path: str
    node_type: str
    depth: int
    child_count: int


class RepositoryStructureSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryStructureResponse(BaseModel):
    repository_path: str
    nodes: list[RepositoryStructureNodeResponse]
    node_count: int
    file_count: int
    directory_count: int
    max_depth: int
    top_level_nodes: list[RepositoryStructureNodeResponse]
    summary: RepositoryStructureSummaryResponse
