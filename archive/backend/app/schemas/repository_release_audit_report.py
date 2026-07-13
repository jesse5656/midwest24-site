from pydantic import BaseModel, Field


class RepositoryReleaseAuditReportRequest(BaseModel):
    package_json: str = Field(..., min_length=2)
    require_accepted: bool = True
    expected_certificate_id: str | None = None
    expected_attestation_id: str | None = None
    expected_baseline_fingerprint: str | None = None
    expected_candidate_fingerprint: str | None = None


class RepositoryReleaseAuditFindingResponse(BaseModel):
    code: str
    severity: str
    message: str


class RepositoryReleaseAuditReportSummaryResponse(BaseModel):
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditReportResponse(BaseModel):
    schema_version: str
    report_id: str
    report_valid: bool
    package_id: str
    repository_name: str
    accepted: bool
    integrity_valid: bool
    passed: bool
    failed: bool
    exit_code: int
    status: str
    certificate_id: str
    attestation_id: str
    findings: list[RepositoryReleaseAuditFindingResponse]
    finding_count: int
    critical_finding_count: int
    error_finding_count: int
    warning_finding_count: int
    finding_codes: list[str]
    report_json: str
    report_markdown: str
    summary: RepositoryReleaseAuditReportSummaryResponse
