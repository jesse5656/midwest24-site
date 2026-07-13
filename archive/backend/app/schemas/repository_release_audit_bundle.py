from pydantic import BaseModel, Field

from app.schemas.repository_snapshot_policy import (
    RepositorySnapshotPolicyData,
)


class RepositoryReleaseAuditBundleRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    baseline_json: str = Field(..., min_length=2)
    policy: RepositorySnapshotPolicyData = Field(
        default_factory=RepositorySnapshotPolicyData
    )
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryReleaseAuditBundleSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditBundleResponse(BaseModel):
    schema_version: str
    repository_path: str
    repository_name: str
    bundle_id: str
    bundle_valid: bool
    accepted: bool
    rejected: bool
    status: str
    exit_code: int
    package_id: str
    package_accepted: bool
    report_id: str
    report_accepted: bool
    certificate_id: str
    attestation_id: str
    failed_component_count: int
    component_names: list[str]
    bundle_json: str
    bundle_markdown: str
    summary: RepositoryReleaseAuditBundleSummaryResponse
