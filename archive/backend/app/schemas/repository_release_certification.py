from pydantic import BaseModel, Field

from app.schemas.repository_snapshot_policy import (
    RepositorySnapshotPolicyData,
)


class RepositoryReleaseCertificationRequest(BaseModel):
    repository_path: str = Field(..., min_length=1)
    baseline_json: str = Field(..., min_length=2)
    policy: RepositorySnapshotPolicyData = Field(
        default_factory=RepositorySnapshotPolicyData
    )
    max_depth: int = Field(default=8, ge=1, le=30)


class RepositoryReleaseCertificationEvidenceResponse(BaseModel):
    name: str
    passed: bool
    severity: str
    message: str


class RepositoryReleaseCertificationSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseCertificationResponse(BaseModel):
    schema_version: str
    repository_path: str
    repository_name: str
    release_ready: bool
    certified: bool
    denied: bool
    status: str
    certificate_id: str
    certificate_valid: bool
    baseline_fingerprint: str
    candidate_fingerprint: str
    evidence: list[
        RepositoryReleaseCertificationEvidenceResponse
    ]
    evidence_count: int
    passed_evidence_count: int
    failed_evidence_count: int
    critical_failure_count: int
    denial_reasons: list[str]
    denial_reason_count: int
    evidence_names: list[str]
    certificate_json: str
    summary: RepositoryReleaseCertificationSummaryResponse
