from pydantic import BaseModel, Field

from app.schemas.repository_snapshot_policy import (
    RepositorySnapshotPolicyData,
)


class RepositoryReleaseEvidencePackageRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    baseline_json: str = Field(..., min_length=2)
    policy: RepositorySnapshotPolicyData = Field(
        default_factory=RepositorySnapshotPolicyData
    )
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryReleaseEvidenceItemResponse(BaseModel):
    name: str
    status: str
    reference: str


class RepositoryReleaseEvidencePackageSummaryResponse(
    BaseModel
):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseEvidencePackageResponse(BaseModel):
    schema_version: str
    repository_path: str
    repository_name: str
    package_id: str
    package_valid: bool
    accepted: bool
    rejected: bool
    status: str
    certificate_id: str
    certificate_accepted: bool
    attestation_id: str
    attestation_accepted: bool
    baseline_fingerprint: str
    candidate_fingerprint: str
    evidence: list[RepositoryReleaseEvidenceItemResponse]
    evidence_count: int
    failed_component_count: int
    component_names: list[str]
    package_json: str
    summary: RepositoryReleaseEvidencePackageSummaryResponse
