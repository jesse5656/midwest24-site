from pydantic import BaseModel, Field


class RepositoryReleaseEvidencePackageVerificationRequest(
    BaseModel
):
    package_json: str = Field(..., min_length=2)
    require_accepted: bool = True
    expected_certificate_id: str | None = None
    expected_attestation_id: str | None = None
    expected_baseline_fingerprint: str | None = None
    expected_candidate_fingerprint: str | None = None


class RepositoryReleaseEvidencePackageVerificationIssueResponse(
    BaseModel
):
    code: str
    severity: str
    message: str


class RepositoryReleaseEvidencePackageVerificationSummaryResponse(
    BaseModel
):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseEvidencePackageVerificationResponse(
    BaseModel
):
    package_id: str
    repository_name: str
    schema_version: str
    certificate_id: str
    attestation_id: str
    integrity_valid: bool
    package_accepted: bool
    valid: bool
    accepted: bool
    rejected: bool
    status: str
    issues: list[
        RepositoryReleaseEvidencePackageVerificationIssueResponse
    ]
    issue_count: int
    critical_issue_count: int
    error_issue_count: int
    warning_issue_count: int
    issue_codes: list[str]
    summary: (
        RepositoryReleaseEvidencePackageVerificationSummaryResponse
    )
