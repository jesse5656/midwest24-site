from pydantic import BaseModel


class RepositoryObjectiveSummaryResponse(BaseModel):
    objective_name: str
    status: str
    total_documents: int
    total_processing_jobs: int
    total_failures: int
    total_duplicates: int
    total_unsupported: int
    total_skipped: int
    action_required: bool
    is_complete: bool
