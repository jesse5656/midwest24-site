from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_audit_ledger_verification import (
    RepositoryReleaseAuditLedgerDocumentVerification,
    RepositoryReleaseAuditLedgerDocumentVerifier,
    RepositoryReleaseAuditLedgerVerificationIssue,
)
from app.connectors.repository.repository_release_audit_ledger_verification_summary import (
    RepositoryReleaseAuditLedgerVerificationSummaryBuilder,
)
from app.schemas.repository_release_audit_ledger_verification import (
    RepositoryReleaseAuditLedgerVerificationIssueResponse,
    RepositoryReleaseAuditLedgerVerificationRequest,
    RepositoryReleaseAuditLedgerVerificationResponse,
    RepositoryReleaseAuditLedgerVerificationSummaryResponse,
)

router = APIRouter()


def serialize_release_audit_ledger_verification_issue(
    issue: RepositoryReleaseAuditLedgerVerificationIssue,
) -> RepositoryReleaseAuditLedgerVerificationIssueResponse:
    return RepositoryReleaseAuditLedgerVerificationIssueResponse(
        code=issue.code,
        severity=issue.severity,
        message=issue.message,
        sequence=issue.sequence,
    )


def serialize_release_audit_ledger_verification(
    verification: RepositoryReleaseAuditLedgerDocumentVerification,
) -> RepositoryReleaseAuditLedgerVerificationResponse:
    summary = (
        RepositoryReleaseAuditLedgerVerificationSummaryBuilder()
        .build(verification)
    )

    return RepositoryReleaseAuditLedgerVerificationResponse(
        ledger_id=verification.ledger_id,
        schema_version=verification.schema_version,
        integrity_valid=verification.integrity_valid,
        chain_valid=verification.chain_valid,
        valid=verification.valid,
        accepted=verification.accepted,
        rejected=verification.rejected,
        status=verification.status,
        entry_count=verification.entry_count,
        accepted_entry_count=(
            verification.accepted_entry_count
        ),
        rejected_entry_count=(
            verification.rejected_entry_count
        ),
        issues=[
            serialize_release_audit_ledger_verification_issue(
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
        invalid_entry_sequences=(
            verification.invalid_entry_sequences
        ),
        summary=(
            RepositoryReleaseAuditLedgerVerificationSummaryResponse(
                outcome=summary.outcome,
                message=summary.message,
                action_required=summary.action_required,
            )
        ),
    )


@router.post(
    "/api/v1/repository-release-audit-ledger-verification",
    response_model=(
        RepositoryReleaseAuditLedgerVerificationResponse
    ),
    status_code=status.HTTP_200_OK,
)
def verify_repository_release_audit_ledger(
    data: RepositoryReleaseAuditLedgerVerificationRequest,
):
    try:
        verification = (
            RepositoryReleaseAuditLedgerDocumentVerifier()
            .verify_json(
                ledger_json=data.ledger_json,
                require_all_accepted=(
                    data.require_all_accepted
                ),
                expected_ledger_id=data.expected_ledger_id,
                expected_bundle_ids=data.expected_bundle_ids,
            )
        )

        return serialize_release_audit_ledger_verification(
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
