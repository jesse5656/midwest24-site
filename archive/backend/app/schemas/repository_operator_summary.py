from pydantic import BaseModel


class RepositoryIngestionOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool
    has_failures: bool
    has_duplicates: bool
    has_unsupported_files: bool
    has_skipped_paths: bool


class RepositoryIncrementalOperatorSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool
    changed_count: int
    ingested_document_count: int
