from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_audit_bundle_verification import (
    RepositoryReleaseAuditBundleVerification,
    RepositoryReleaseAuditBundleVerificationIssue,
    RepositoryReleaseAuditBundleVerifier,
)
from app.connectors.repository.repository_release_audit_bundle_verification_summary import (
    RepositoryReleaseAuditBundleVerificationSummaryBuilder,
)
from app.schemas.repository_release_audit_bundle_verification import (
    RepositoryReleaseAuditBundleVerificationIssueResponse,
    RepositoryReleaseAuditBundleVerificationRequest,
    RepositoryReleaseAuditBundleVerificationResponse,
    RepositoryReleaseAuditBundleVerificationSummaryResponse,
)

router = APIRouter()


def serialize_release_audit_bundle_verification_issue(
    issue: RepositoryReleaseAuditBundleVerificationIssue,
) -> RepositoryReleaseAuditBundleVerificationIssueResponse:
    return RepositoryReleaseAuditBundleVerificationIssueResponse(
        code=issue.code,
        severity=issue.severity,
        message=issue.message,
    )


def serialize_release_audit_bundle_verification(
    verification: RepositoryReleaseAuditBundleVerification,
) -> RepositoryReleaseAuditBundleVerificationResponse:
    summary = (
        RepositoryReleaseAuditBundleVerificationSummaryBuilder()
        .build(verification)
    )

    return RepositoryReleaseAuditBundleVerificationResponse(
        bundle_id=verification.bundle_id,
        package_id=verification.package_id,
        report_id=verification.report_id,
        certificate_id=verification.certificate_id,
        attestation_id=verification.attestation_id,
        repository_name=verification.repository_name,
        schema_version=verification.schema_version,
        bundle_accepted=verification.bundle_accepted,
        integrity_valid=verification.integrity_valid,
        valid=verification.valid,
        accepted=verification.accepted,
        rejected=verification.rejected,
        status=verification.status,
        issues=[
            serialize_release_audit_bundle_verification_issue(
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
            RepositoryReleaseAuditBundleVerificationSummaryResponse(
                outcome=summary.outcome,
                message=summary.message,
                action_required=summary.action_required,
            )
        ),
    )


@router.post(
    "/api/v1/repository-release-audit-bundle-verification",
    response_model=(
        RepositoryReleaseAuditBundleVerificationResponse
    ),
    status_code=status.HTTP_200_OK,
)
def verify_repository_release_audit_bundle(
    data: RepositoryReleaseAuditBundleVerificationRequest,
):
    try:
        verification = (
            RepositoryReleaseAuditBundleVerifier()
            .verify_json(
                bundle_json=data.bundle_json,
                require_accepted=data.require_accepted,
                expected_package_id=(
                    data.expected_package_id
                ),
                expected_report_id=(
                    data.expected_report_id
                ),
                expected_certificate_id=(
                    data.expected_certificate_id
                ),
                expected_attestation_id=(
                    data.expected_attestation_id
                ),
                expected_baseline_fingerprint=(
                    data.expected_baseline_fingerprint
                ),
                expected_candidate_fingerprint=(
                    data.expected_candidate_fingerprint
                ),
            )
        )

        return serialize_release_audit_bundle_verification(
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
