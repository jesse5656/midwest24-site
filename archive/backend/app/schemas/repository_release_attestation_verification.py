from pydantic import BaseModel, Field


class RepositoryReleaseAttestationVerificationRequest(BaseModel):
    attestation_json: str = Field(..., min_length=2)
    require_accepted: bool = True
    expected_certificate_id: str | None = None
    expected_baseline_fingerprint: str | None = None
    expected_candidate_fingerprint: str | None = None


class RepositoryReleaseAttestationVerificationIssueResponse(
    BaseModel
):
    code: str
    severity: str
    message: str


class RepositoryReleaseAttestationVerificationSummaryResponse(
    BaseModel
):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAttestationVerificationResponse(
    BaseModel
):
    attestation_id: str
    certificate_id: str
    repository_name: str
    schema_version: str
    certified: bool
    certificate_valid: bool
    integrity_valid: bool
    valid: bool
    accepted: bool
    rejected: bool
    status: str
    issues: list[
        RepositoryReleaseAttestationVerificationIssueResponse
    ]
    issue_count: int
    critical_issue_count: int
    error_issue_count: int
    warning_issue_count: int
    issue_codes: list[str]
    summary: (
        RepositoryReleaseAttestationVerificationSummaryResponse
    )
