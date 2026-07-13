from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_audit_ledger_snapshot import (
    RepositoryReleaseAuditLedgerSnapshot,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerSnapshotSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerSnapshotSummaryBuilder:
    def build(
        self,
        snapshot: RepositoryReleaseAuditLedgerSnapshot,
    ) -> RepositoryReleaseAuditLedgerSnapshotSummary:
        if snapshot.accepted:
            return RepositoryReleaseAuditLedgerSnapshotSummary(
                outcome="ledger_snapshot_accepted",
                message=(
                    f"Release audit ledger snapshot "
                    f"{snapshot.snapshot_id[:12]} is valid with "
                    f"{snapshot.entry_count} accepted entry "
                    f"or entries."
                ),
                action_required=False,
            )

        if not snapshot.ledger_integrity_valid:
            return RepositoryReleaseAuditLedgerSnapshotSummary(
                outcome="ledger_snapshot_invalid_integrity",
                message=(
                    "Release audit ledger snapshot was rejected "
                    "because the source ledger failed integrity "
                    "verification."
                ),
                action_required=True,
            )

        if not snapshot.ledger_chain_valid:
            return RepositoryReleaseAuditLedgerSnapshotSummary(
                outcome="ledger_snapshot_invalid_chain",
                message=(
                    "Release audit ledger snapshot was rejected "
                    "because the source ledger chain is invalid."
                ),
                action_required=True,
            )

        return RepositoryReleaseAuditLedgerSnapshotSummary(
            outcome="ledger_snapshot_rejected",
            message=(
                f"Release audit ledger snapshot contains "
                f"{snapshot.rejected_entry_count} rejected entry "
                f"or entries and {snapshot.issue_count} issue(s)."
            ),
            action_required=True,
        )
