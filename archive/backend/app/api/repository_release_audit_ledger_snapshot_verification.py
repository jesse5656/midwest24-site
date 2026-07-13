from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_audit_ledger_snapshot_verification import (
    RepositoryReleaseAuditLedgerSnapshotVerification,
    RepositoryReleaseAuditLedgerSnapshotVerificationIssue,
    RepositoryReleaseAuditLedgerSnapshotVerifier,
)
from app.connectors.repository.repository_release_audit_ledger_snapshot_verification_summary import (
    RepositoryReleaseAuditLedgerSnapshotVerificationSummaryBuilder,
)
from app.schemas.repository_release_audit_ledger_snapshot_verification import (
    RepositoryReleaseAuditLedgerSnapshotVerificationIssueResponse,
    RepositoryReleaseAuditLedgerSnapshotVerificationRequest,
    RepositoryReleaseAuditLedgerSnapshotVerificationResponse,
    RepositoryReleaseAuditLedgerSnapshotVerificationSummaryResponse,
)

router = APIRouter()


def serialize_ledger_snapshot_verification_issue(
    issue: RepositoryReleaseAuditLedgerSnapshotVerificationIssue,
) -> RepositoryReleaseAuditLedgerSnapshotVerificationIssueResponse:
    return RepositoryReleaseAuditLedgerSnapshotVerificationIssueResponse(
        code=issue.code,
        severity=issue.severity,
        message=issue.message,
        sequence=issue.sequence,
    )


def serialize_ledger_snapshot_verification(
    verification: RepositoryReleaseAuditLedgerSnapshotVerification,
) -> RepositoryReleaseAuditLedgerSnapshotVerificationResponse:
    summary = (
        RepositoryReleaseAuditLedgerSnapshotVerificationSummaryBuilder()
        .build(verification)
    )

    return RepositoryReleaseAuditLedgerSnapshotVerificationResponse(
        snapshot_id=verification.snapshot_id,
        ledger_id=verification.ledger_id,
        schema_version=verification.schema_version,
        snapshot_accepted=verification.snapshot_accepted,
        integrity_valid=verification.integrity_valid,
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
        repository_count=verification.repository_count,
        issues=[
            serialize_ledger_snapshot_verification_issue(
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
            RepositoryReleaseAuditLedgerSnapshotVerificationSummaryResponse(
                outcome=summary.outcome,
                message=summary.message,
                action_required=summary.action_required,
            )
        ),
    )


@router.post(
    "/api/v1/repository-release-audit-ledger-snapshot-verification",
    response_model=(
        RepositoryReleaseAuditLedgerSnapshotVerificationResponse
    ),
    status_code=status.HTTP_200_OK,
)
def verify_repository_release_audit_ledger_snapshot(
    data: RepositoryReleaseAuditLedgerSnapshotVerificationRequest,
):
    try:
        verification = (
            RepositoryReleaseAuditLedgerSnapshotVerifier()
            .verify_json(
                snapshot_json=data.snapshot_json,
                require_accepted=data.require_accepted,
                expected_snapshot_id=data.expected_snapshot_id,
                expected_ledger_id=data.expected_ledger_id,
                expected_latest_entry_hash=(
                    data.expected_latest_entry_hash
                ),
                expected_bundle_ids=data.expected_bundle_ids,
            )
        )

        return serialize_ledger_snapshot_verification(
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
