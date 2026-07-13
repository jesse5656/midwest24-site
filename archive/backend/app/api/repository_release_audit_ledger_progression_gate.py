from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_audit_ledger_progression_gate import (
    RepositoryReleaseAuditLedgerProgressionGate,
    RepositoryReleaseAuditLedgerProgressionGateEvaluator,
    RepositoryReleaseAuditLedgerProgressionGateReason,
)
from app.connectors.repository.repository_release_audit_ledger_progression_gate_summary import (
    RepositoryReleaseAuditLedgerProgressionGateSummaryBuilder,
)
from app.schemas.repository_release_audit_ledger_progression_gate import (
    RepositoryReleaseAuditLedgerProgressionGateReasonResponse,
    RepositoryReleaseAuditLedgerProgressionGateRequest,
    RepositoryReleaseAuditLedgerProgressionGateResponse,
    RepositoryReleaseAuditLedgerProgressionGateSummaryResponse,
)

router = APIRouter()


def serialize_ledger_progression_gate_reason(
    reason: RepositoryReleaseAuditLedgerProgressionGateReason,
) -> RepositoryReleaseAuditLedgerProgressionGateReasonResponse:
    return (
        RepositoryReleaseAuditLedgerProgressionGateReasonResponse(
            code=reason.code,
            severity=reason.severity,
            message=reason.message,
        )
    )


def serialize_ledger_progression_gate(
    gate: RepositoryReleaseAuditLedgerProgressionGate,
) -> RepositoryReleaseAuditLedgerProgressionGateResponse:
    comparison = gate.comparison

    summary = (
        RepositoryReleaseAuditLedgerProgressionGateSummaryBuilder()
        .build(gate)
    )

    return RepositoryReleaseAuditLedgerProgressionGateResponse(
        baseline_snapshot_id=(
            comparison.baseline_snapshot_id
        ),
        candidate_snapshot_id=(
            comparison.candidate_snapshot_id
        ),
        baseline_valid=(
            comparison.baseline_verification.valid
        ),
        candidate_valid=(
            comparison.candidate_verification.valid
        ),
        baseline_accepted=(
            comparison.baseline_verification.accepted
        ),
        candidate_accepted=(
            comparison.candidate_verification.accepted
        ),
        snapshots_identical=comparison.snapshots_identical,
        append_only=comparison.append_only,
        history_rewritten=comparison.history_rewritten,
        acceptance_regression=(
            comparison.acceptance_regression
        ),
        safe_progression=comparison.safe_progression,
        entry_count_delta=comparison.entry_count_delta,
        added_bundle_ids=comparison.added_bundle_ids,
        removed_bundle_ids=comparison.removed_bundle_ids,
        allow_unchanged=gate.allow_unchanged,
        require_candidate_accepted=(
            gate.require_candidate_accepted
        ),
        passed=gate.passed,
        blocked=gate.blocked,
        exit_code=gate.exit_code,
        status=gate.status,
        reasons=[
            serialize_ledger_progression_gate_reason(reason)
            for reason in gate.reasons
        ],
        reason_count=gate.reason_count,
        critical_reason_count=gate.critical_reason_count,
        error_reason_count=gate.error_reason_count,
        warning_reason_count=gate.warning_reason_count,
        reason_codes=gate.reason_codes,
        summary=(
            RepositoryReleaseAuditLedgerProgressionGateSummaryResponse(
                outcome=summary.outcome,
                message=summary.message,
                action_required=summary.action_required,
            )
        ),
    )


@router.post(
    "/api/v1/repository-release-audit-ledger-progression-gate",
    response_model=(
        RepositoryReleaseAuditLedgerProgressionGateResponse
    ),
    status_code=status.HTTP_200_OK,
)
def evaluate_repository_release_audit_ledger_progression(
    data: RepositoryReleaseAuditLedgerProgressionGateRequest,
):
    try:
        gate = (
            RepositoryReleaseAuditLedgerProgressionGateEvaluator()
            .evaluate(
                baseline_snapshot_json=(
                    data.baseline_snapshot_json
                ),
                candidate_snapshot_json=(
                    data.candidate_snapshot_json
                ),
                allow_unchanged=data.allow_unchanged,
                require_candidate_accepted=(
                    data.require_candidate_accepted
                ),
            )
        )

        return serialize_ledger_progression_gate(gate)

    except (
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
