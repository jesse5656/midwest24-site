from pydantic import BaseModel, Field


class RepositoryReleaseAuditReportVerificationRequest(
    BaseModel
):
    report_json: str = Field(..., min_length=2)
    require_passed: bool = True
    expected_package_id: str | None = None
    expected_certificate_id: str | None = None
    expected_attestation_id: str | None = None


class RepositoryReleaseAuditReportVerificationIssueResponse(
    BaseModel
):
    code: str
    severity: str
    message: str


class RepositoryReleaseAuditReportVerificationSummaryResponse(
    BaseModel
):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditReportVerificationResponse(
    BaseModel
):
    report_id: str
    package_id: str
    certificate_id: str
    attestation_id: str
    repository_name: str
    schema_version: str
    report_passed: bool
    integrity_valid: bool
    valid: bool
    accepted: bool
    rejected: bool
    status: str
    issues: list[
        RepositoryReleaseAuditReportVerificationIssueResponse
    ]
    issue_count: int
    critical_issue_count: int
    error_issue_count: int
    warning_issue_count: int
    issue_codes: list[str]
    summary: (
        RepositoryReleaseAuditReportVerificationSummaryResponse
    )
