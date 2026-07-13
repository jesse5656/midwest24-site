from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_audit_report_verification import (
    RepositoryReleaseAuditReportVerification,
    RepositoryReleaseAuditReportVerificationIssue,
    RepositoryReleaseAuditReportVerifier,
)
from app.connectors.repository.repository_release_audit_report_verification_summary import (
    RepositoryReleaseAuditReportVerificationSummaryBuilder,
)
from app.schemas.repository_release_audit_report_verification import (
    RepositoryReleaseAuditReportVerificationIssueResponse,
    RepositoryReleaseAuditReportVerificationRequest,
    RepositoryReleaseAuditReportVerificationResponse,
    RepositoryReleaseAuditReportVerificationSummaryResponse,
)

router = APIRouter()


def serialize_release_audit_report_verification_issue(
    issue: RepositoryReleaseAuditReportVerificationIssue,
) -> RepositoryReleaseAuditReportVerificationIssueResponse:
    return RepositoryReleaseAuditReportVerificationIssueResponse(
        code=issue.code,
        severity=issue.severity,
        message=issue.message,
    )


def serialize_release_audit_report_verification(
    verification: RepositoryReleaseAuditReportVerification,
) -> RepositoryReleaseAuditReportVerificationResponse:
    summary = (
        RepositoryReleaseAuditReportVerificationSummaryBuilder()
        .build(verification)
    )

    return RepositoryReleaseAuditReportVerificationResponse(
        report_id=verification.report_id,
        package_id=verification.package_id,
        certificate_id=verification.certificate_id,
        attestation_id=verification.attestation_id,
        repository_name=verification.repository_name,
        schema_version=verification.schema_version,
        report_passed=verification.report_passed,
        integrity_valid=verification.integrity_valid,
        valid=verification.valid,
        accepted=verification.accepted,
        rejected=verification.rejected,
        status=verification.status,
        issues=[
            serialize_release_audit_report_verification_issue(
                issue
            )
            for issue in verification.issues
        ],
        issue_count=verification.issue_count,
        critical_issue_count=(
            verification.critical_issue_count
        ),
        error_issue_count=verification.error_issue_count,
        warning_issue_count=(
            verification.warning_issue_count
        ),
        issue_codes=verification.issue_codes,
        summary=(
            RepositoryReleaseAuditReportVerificationSummaryResponse(
                outcome=summary.outcome,
                message=summary.message,
                action_required=summary.action_required,
            )
        ),
    )


@router.post(
    "/api/v1/repository-release-audit-report-verification",
    response_model=(
        RepositoryReleaseAuditReportVerificationResponse
    ),
    status_code=status.HTTP_200_OK,
)
def verify_repository_release_audit_report(
    data: RepositoryReleaseAuditReportVerificationRequest,
):
    try:
        verification = (
            RepositoryReleaseAuditReportVerifier()
            .verify_json(
                report_json=data.report_json,
                require_passed=data.require_passed,
                expected_package_id=(
                    data.expected_package_id
                ),
                expected_certificate_id=(
                    data.expected_certificate_id
                ),
                expected_attestation_id=(
                    data.expected_attestation_id
                ),
            )
        )

        return serialize_release_audit_report_verification(
            verification
        )

    except (
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
