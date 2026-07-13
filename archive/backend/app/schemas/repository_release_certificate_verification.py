from pydantic import BaseModel, Field


class RepositoryReleaseCertificateVerificationRequest(BaseModel):
    certificate_json: str = Field(..., min_length=2)
    require_certified: bool = True
    expected_baseline_fingerprint: str | None = None
    expected_candidate_fingerprint: str | None = None


class RepositoryReleaseCertificateVerificationIssueResponse(
    BaseModel
):
    code: str
    severity: str
    message: str


class RepositoryReleaseCertificateVerificationSummaryResponse(
    BaseModel
):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseCertificateVerificationResponse(
    BaseModel
):
    certificate_id: str
    repository_name: str
    schema_version: str
    certified: bool
    integrity_valid: bool
    valid: bool
    accepted: bool
    status: str
    issues: list[
        RepositoryReleaseCertificateVerificationIssueResponse
    ]
    issue_count: int
    critical_issue_count: int
    error_issue_count: int
    warning_issue_count: int
    issue_codes: list[str]
    summary: (
        RepositoryReleaseCertificateVerificationSummaryResponse
    )
