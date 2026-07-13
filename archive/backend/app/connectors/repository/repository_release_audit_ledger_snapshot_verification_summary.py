from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_audit_ledger_snapshot_verification import (
    RepositoryReleaseAuditLedgerSnapshotVerification,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerSnapshotVerificationSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerSnapshotVerificationSummaryBuilder:
    def build(
        self,
        verification: RepositoryReleaseAuditLedgerSnapshotVerification,
    ) -> RepositoryReleaseAuditLedgerSnapshotVerificationSummary:
        if verification.accepted:
            return RepositoryReleaseAuditLedgerSnapshotVerificationSummary(
                outcome="ledger_snapshot_accepted",
                message=(
                    f"Ledger snapshot "
                    f"{verification.snapshot_id[:12]} is valid with "
                    f"{verification.entry_count} accepted entry "
                    f"or entries."
                ),
                action_required=False,
            )

        if verification.critical_issue_count > 0:
            return RepositoryReleaseAuditLedgerSnapshotVerificationSummary(
                outcome="ledger_snapshot_rejected_critical",
                message=(
                    f"Ledger snapshot verification failed with "
                    f"{verification.issue_count} issue(s), including "
                    f"{verification.critical_issue_count} critical."
                ),
                action_required=True,
            )

        if verification.valid:
            return RepositoryReleaseAuditLedgerSnapshotVerificationSummary(
                outcome="ledger_snapshot_valid_not_accepted",
                message=(
                    "Ledger snapshot integrity is valid, but the "
                    "snapshot is not accepted."
                ),
                action_required=True,
            )

        return RepositoryReleaseAuditLedgerSnapshotVerificationSummary(
            outcome="ledger_snapshot_rejected",
            message=(
                f"Ledger snapshot verification failed with "
                f"{verification.issue_count} issue(s)."
            ),
            action_required=True,
        )
