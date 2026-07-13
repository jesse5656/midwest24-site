from pydantic import BaseModel, Field

from app.schemas.repository_snapshot_policy import (
    RepositorySnapshotPolicyData,
)


class RepositoryReleaseAttestationRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    baseline_json: str = Field(..., min_length=2)
    policy: RepositorySnapshotPolicyData = Field(
        default_factory=RepositorySnapshotPolicyData
    )
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryReleaseAttestationEvidenceResponse(BaseModel):
    name: str
    passed: bool
    severity: str
    message: str


class RepositoryReleaseAttestationSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAttestationResponse(BaseModel):
    schema_version: str
    repository_path: str
    repository_name: str
    attestation_id: str
    attestation_valid: bool
    certificate_id: str
    certificate_valid: bool
    certified: bool
    accepted: bool
    rejected: bool
    status: str
    baseline_fingerprint: str
    candidate_fingerprint: str
    evidence: list[
        RepositoryReleaseAttestationEvidenceResponse
    ]
    evidence_count: int
    passed_evidence_count: int
    failed_evidence_count: int
    evidence_names: list[str]
    issues: list[str]
    issue_count: int
    attestation_json: str
    summary: RepositoryReleaseAttestationSummaryResponse
