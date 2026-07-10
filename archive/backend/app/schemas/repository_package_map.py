from pydantic import BaseModel, Field


class RepositoryPackageMapRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=5, ge=1, le=20)


class RepositoryPackageMarkerResponse(BaseModel):
    path: str
    marker_name: str
    ecosystem: str
    depth: int


class RepositoryPackageMapSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryPackageMapResponse(BaseModel):
    repository_path: str
    markers: list[RepositoryPackageMarkerResponse]
    marker_count: int
    ecosystem_count: int
    ecosystems: list[str]
    root_markers: list[RepositoryPackageMarkerResponse]
    summary: RepositoryPackageMapSummaryResponse
