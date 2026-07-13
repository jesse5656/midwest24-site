from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_attestation_verification import (
    RepositoryReleaseAttestationVerification,
    RepositoryReleaseAttestationVerificationIssue,
    RepositoryReleaseAttestationVerifier,
)
from app.connectors.repository.repository_release_attestation_verification_summary import (
    RepositoryReleaseAttestationVerificationSummaryBuilder,
)
from app.schemas.repository_release_attestation_verification import (
    RepositoryReleaseAttestationVerificationIssueResponse,
    RepositoryReleaseAttestationVerificationRequest,
    RepositoryReleaseAttestationVerificationResponse,
    RepositoryReleaseAttestationVerificationSummaryResponse,
)

router = APIRouter()


def serialize_release_attestation_verification_issue(
    issue: RepositoryReleaseAttestationVerificationIssue,
) -> RepositoryReleaseAttestationVerificationIssueResponse:
    return RepositoryReleaseAttestationVerificationIssueResponse(
        code=issue.code,
        severity=issue.severity,
        message=issue.message,
    )


def serialize_release_attestation_verification(
    verification: RepositoryReleaseAttestationVerification,
) -> RepositoryReleaseAttestationVerificationResponse:
    summary = (
        RepositoryReleaseAttestationVerificationSummaryBuilder()
        .build(verification)
    )

    return RepositoryReleaseAttestationVerificationResponse(
        attestation_id=verification.attestation_id,
        certificate_id=verification.certificate_id,
        repository_name=verification.repository_name,
        schema_version=verification.schema_version,
        certified=verification.certified,
        certificate_valid=verification.certificate_valid,
        integrity_valid=verification.integrity_valid,
        valid=verification.valid,
        accepted=verification.accepted,
        rejected=verification.rejected,
        status=verification.status,
        issues=[
            serialize_release_attestation_verification_issue(
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
            RepositoryReleaseAttestationVerificationSummaryResponse(
                outcome=summary.outcome,
                message=summary.message,
                action_required=summary.action_required,
            )
        ),
    )


@router.post(
    "/api/v1/repository-release-attestation-verification",
    response_model=(
        RepositoryReleaseAttestationVerificationResponse
    ),
    status_code=status.HTTP_200_OK,
)
def verify_repository_release_attestation(
    data: RepositoryReleaseAttestationVerificationRequest,
):
    try:
        verification = (
            RepositoryReleaseAttestationVerifier()
            .verify_json(
                attestation_json=data.attestation_json,
                require_accepted=data.require_accepted,
                expected_certificate_id=(
                    data.expected_certificate_id
                ),
                expected_baseline_fingerprint=(
                    data.expected_baseline_fingerprint
                ),
                expected_candidate_fingerprint=(
                    data.expected_candidate_fingerprint
                ),
            )
        )

        return serialize_release_attestation_verification(
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
