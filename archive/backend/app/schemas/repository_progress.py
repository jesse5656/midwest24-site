from pydantic import BaseModel, Field


class RepositoryProgressCheckpointRequest(BaseModel):
    name: str = Field(..., min_length=1)
    test_count: int = Field(..., ge=0)
    status: str = Field(..., min_length=1)
    notes: str = ""


class RepositoryProgressCheckpointResponse(BaseModel):
    name: str
    test_count: int
    status: str
    notes: str


class RepositoryProgressLedgerResponse(BaseModel):
    repository: str
    checkpoints: list[RepositoryProgressCheckpointResponse]
    latest_test_count: int
    checkpoint_count: int
    completed_count: int


class RepositoryProgressSummaryResponse(BaseModel):
    repository: str
    latest_test_count: int
    checkpoint_count: int
    completed_count: int
    status: str
    message: str
