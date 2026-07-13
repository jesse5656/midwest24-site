from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_audit_ledger_verification import (
    RepositoryReleaseAuditLedgerDocumentVerification,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerVerificationSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerVerificationSummaryBuilder:
    def build(
        self,
        verification: RepositoryReleaseAuditLedgerDocumentVerification,
    ) -> RepositoryReleaseAuditLedgerVerificationSummary:
        if verification.accepted:
            return RepositoryReleaseAuditLedgerVerificationSummary(
                outcome="release_audit_ledger_accepted",
                message=(
                    f"Release audit ledger "
                    f"{verification.ledger_id[:12]} is valid with "
                    f"{verification.entry_count} accepted entry "
                    f"or entries."
                ),
                action_required=False,
            )

        if verification.critical_issue_count > 0:
            return RepositoryReleaseAuditLedgerVerificationSummary(
                outcome="release_audit_ledger_rejected_critical",
                message=(
                    f"Release audit ledger verification failed with "
                    f"{verification.issue_count} issue(s), including "
                    f"{verification.critical_issue_count} critical."
                ),
                action_required=True,
            )

        if verification.valid:
            return RepositoryReleaseAuditLedgerVerificationSummary(
                outcome="release_audit_ledger_valid_not_accepted",
                message=(
                    "Release audit ledger integrity is valid, but "
                    f"the ledger contains "
                    f"{verification.rejected_entry_count} rejected "
                    f"entry or entries."
                ),
                action_required=True,
            )

        return RepositoryReleaseAuditLedgerVerificationSummary(
            outcome="release_audit_ledger_rejected",
            message=(
                f"Release audit ledger verification failed with "
                f"{verification.issue_count} issue(s)."
            ),
            action_required=True,
        )
