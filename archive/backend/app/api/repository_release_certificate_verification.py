from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_certificate_verification import (
    RepositoryReleaseCertificateVerification,
    RepositoryReleaseCertificateVerificationIssue,
    RepositoryReleaseCertificateVerifier,
)
from app.connectors.repository.repository_release_certificate_verification_summary import (
    RepositoryReleaseCertificateVerificationSummaryBuilder,
)
from app.schemas.repository_release_certificate_verification import (
    RepositoryReleaseCertificateVerificationIssueResponse,
    RepositoryReleaseCertificateVerificationRequest,
    RepositoryReleaseCertificateVerificationResponse,
    RepositoryReleaseCertificateVerificationSummaryResponse,
)

router = APIRouter()


def serialize_release_certificate_verification_issue(
    issue: RepositoryReleaseCertificateVerificationIssue,
) -> RepositoryReleaseCertificateVerificationIssueResponse:
    return RepositoryReleaseCertificateVerificationIssueResponse(
        code=issue.code,
        severity=issue.severity,
        message=issue.message,
    )


def serialize_release_certificate_verification(
    verification: RepositoryReleaseCertificateVerification,
) -> RepositoryReleaseCertificateVerificationResponse:
    summary = (
        RepositoryReleaseCertificateVerificationSummaryBuilder()
        .build(verification)
    )

    return RepositoryReleaseCertificateVerificationResponse(
        certificate_id=verification.certificate_id,
        repository_name=verification.repository_name,
        schema_version=verification.schema_version,
        certified=verification.certified,
        integrity_valid=verification.integrity_valid,
        valid=verification.valid,
        accepted=verification.accepted,
        status=verification.status,
        issues=[
            serialize_release_certificate_verification_issue(
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
            RepositoryReleaseCertificateVerificationSummaryResponse(
                outcome=summary.outcome,
                message=summary.message,
                action_required=summary.action_required,
            )
        ),
    )


@router.post(
    "/api/v1/repository-release-certificate-verification",
    response_model=(
        RepositoryReleaseCertificateVerificationResponse
    ),
    status_code=status.HTTP_200_OK,
)
def verify_repository_release_certificate(
    data: RepositoryReleaseCertificateVerificationRequest,
):
    try:
        verification = (
            RepositoryReleaseCertificateVerifier()
            .verify_json(
                certificate_json=data.certificate_json,
                require_certified=data.require_certified,
                expected_baseline_fingerprint=(
                    data.expected_baseline_fingerprint
                ),
                expected_candidate_fingerprint=(
                    data.expected_candidate_fingerprint
                ),
            )
        )

        return serialize_release_certificate_verification(
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
