from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_evidence_package_verification import (
    RepositoryReleaseEvidencePackageVerification,
    RepositoryReleaseEvidencePackageVerificationIssue,
    RepositoryReleaseEvidencePackageVerifier,
)
from app.connectors.repository.repository_release_evidence_package_verification_summary import (
    RepositoryReleaseEvidencePackageVerificationSummaryBuilder,
)
from app.schemas.repository_release_evidence_package_verification import (
    RepositoryReleaseEvidencePackageVerificationIssueResponse,
    RepositoryReleaseEvidencePackageVerificationRequest,
    RepositoryReleaseEvidencePackageVerificationResponse,
    RepositoryReleaseEvidencePackageVerificationSummaryResponse,
)

router = APIRouter()


def serialize_release_evidence_package_verification_issue(
    issue: RepositoryReleaseEvidencePackageVerificationIssue,
) -> RepositoryReleaseEvidencePackageVerificationIssueResponse:
    return RepositoryReleaseEvidencePackageVerificationIssueResponse(
        code=issue.code,
        severity=issue.severity,
        message=issue.message,
    )


def serialize_release_evidence_package_verification(
    verification: RepositoryReleaseEvidencePackageVerification,
) -> RepositoryReleaseEvidencePackageVerificationResponse:
    summary = (
        RepositoryReleaseEvidencePackageVerificationSummaryBuilder()
        .build(verification)
    )

    return RepositoryReleaseEvidencePackageVerificationResponse(
        package_id=verification.package_id,
        repository_name=verification.repository_name,
        schema_version=verification.schema_version,
        certificate_id=verification.certificate_id,
        attestation_id=verification.attestation_id,
        integrity_valid=verification.integrity_valid,
        package_accepted=verification.package_accepted,
        valid=verification.valid,
        accepted=verification.accepted,
        rejected=verification.rejected,
        status=verification.status,
        issues=[
            serialize_release_evidence_package_verification_issue(
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
            RepositoryReleaseEvidencePackageVerificationSummaryResponse(
                outcome=summary.outcome,
                message=summary.message,
                action_required=summary.action_required,
            )
        ),
    )


@router.post(
    "/api/v1/repository-release-evidence-package-verification",
    response_model=(
        RepositoryReleaseEvidencePackageVerificationResponse
    ),
    status_code=status.HTTP_200_OK,
)
def verify_repository_release_evidence_package(
    data: RepositoryReleaseEvidencePackageVerificationRequest,
):
    try:
        verification = (
            RepositoryReleaseEvidencePackageVerifier()
            .verify_json(
                package_json=data.package_json,
                require_accepted=data.require_accepted,
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

        return serialize_release_evidence_package_verification(
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
