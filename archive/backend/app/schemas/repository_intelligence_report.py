from pydantic import BaseModel, Field


class RepositoryIntelligenceReportRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryIntelligenceReportSectionResponse(BaseModel):
    name: str
    content: str
    status: str


class RepositoryIntelligenceReportSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryIntelligenceReportResponse(BaseModel):
    repository_path: str
    repository_name: str
    title: str
    sections: list[
        RepositoryIntelligenceReportSectionResponse
    ]
    section_count: int
    section_names: list[str]
    info_count: int
    warning_count: int
    critical_count: int
    is_healthy: bool
    markdown: str
    summary: RepositoryIntelligenceReportSummaryResponse
