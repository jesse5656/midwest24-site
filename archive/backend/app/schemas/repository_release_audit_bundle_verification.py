from pydantic import BaseModel, Field


class RepositoryReleaseAuditBundleVerificationRequest(
    BaseModel
):
    bundle_json: str = Field(..., min_length=2)
    require_accepted: bool = True
    expected_package_id: str | None = None
    expected_report_id: str | None = None
    expected_certificate_id: str | None = None
    expected_attestation_id: str | None = None
    expected_baseline_fingerprint: str | None = None
    expected_candidate_fingerprint: str | None = None


class RepositoryReleaseAuditBundleVerificationIssueResponse(
    BaseModel
):
    code: str
    severity: str
    message: str


class RepositoryReleaseAuditBundleVerificationSummaryResponse(
    BaseModel
):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditBundleVerificationResponse(
    BaseModel
):
    bundle_id: str
    package_id: str
    report_id: str
    certificate_id: str
    attestation_id: str
    repository_name: str
    schema_version: str
    bundle_accepted: bool
    integrity_valid: bool
    valid: bool
    accepted: bool
    rejected: bool
    status: str
    issues: list[
        RepositoryReleaseAuditBundleVerificationIssueResponse
    ]
    issue_count: int
    critical_issue_count: int
    error_issue_count: int
    warning_issue_count: int
    issue_codes: list[str]
    summary: (
        RepositoryReleaseAuditBundleVerificationSummaryResponse
    )
