from pydantic import BaseModel


class GitIntelligenceProgressResponse(BaseModel):
    objective_name: str
    capability_count: int
    endpoint_count: int
    test_count: int
    status: str
    ready_for_closeout: bool
