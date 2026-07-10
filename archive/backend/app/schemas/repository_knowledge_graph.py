from pydantic import BaseModel, Field


class RepositoryKnowledgeGraphRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryKnowledgeGraphNodeResponse(BaseModel):
    node_id: str
    node_type: str
    label: str
    source: str


class RepositoryKnowledgeGraphEdgeResponse(BaseModel):
    source_id: str
    target_id: str
    relationship: str


class RepositoryKnowledgeGraphSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryKnowledgeGraphResponse(BaseModel):
    repository_path: str
    nodes: list[RepositoryKnowledgeGraphNodeResponse]
    edges: list[RepositoryKnowledgeGraphEdgeResponse]
    node_count: int
    edge_count: int
    node_types: list[str]
    relationship_types: list[str]
    file_node_count: int
    package_node_count: int
    dependency_node_count: int
    symbol_node_count: int
    import_node_count: int
    summary: RepositoryKnowledgeGraphSummaryResponse
