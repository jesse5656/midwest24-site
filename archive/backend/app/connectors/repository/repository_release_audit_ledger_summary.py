from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_audit_ledger import (
    RepositoryReleaseAuditLedger,
    RepositoryReleaseAuditLedgerVerification,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerSummaryBuilder:
    def build(
        self,
        ledger: RepositoryReleaseAuditLedger,
        verification: RepositoryReleaseAuditLedgerVerification,
    ) -> RepositoryReleaseAuditLedgerSummary:
        if not verification.valid:
            return RepositoryReleaseAuditLedgerSummary(
                outcome="ledger_invalid",
                message=(
                    f"Release audit ledger failed integrity "
                    f"verification at "
                    f"{len(verification.invalid_entry_sequences)} "
                    f"entry sequence(s)."
                ),
                action_required=True,
            )

        if ledger.entry_count == 0:
            return RepositoryReleaseAuditLedgerSummary(
                outcome="ledger_empty",
                message="Release audit ledger contains no entries.",
                action_required=True,
            )

        if ledger.rejected_entry_count > 0:
            return RepositoryReleaseAuditLedgerSummary(
                outcome="ledger_contains_rejections",
                message=(
                    f"Release audit ledger is valid but contains "
                    f"{ledger.rejected_entry_count} rejected entry "
                    f"or entries."
                ),
                action_required=True,
            )

        return RepositoryReleaseAuditLedgerSummary(
            outcome="ledger_accepted",
            message=(
                f"Release audit ledger "
                f"{ledger.ledger_id[:12]} is valid with "
                f"{ledger.entry_count} accepted entry or entries."
            ),
            action_required=False,
        )
