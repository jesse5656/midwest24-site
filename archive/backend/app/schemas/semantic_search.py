from pydantic import BaseModel, Field


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=50)


class SemanticSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    entity_id: str
    entity_title: str
    filename: str
    text: str
    distance: float
