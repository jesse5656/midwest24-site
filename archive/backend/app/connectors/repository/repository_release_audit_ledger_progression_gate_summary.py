from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_audit_ledger_progression_gate import (
    RepositoryReleaseAuditLedgerProgressionGate,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerProgressionGateSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerProgressionGateSummaryBuilder:
    def build(
        self,
        gate: RepositoryReleaseAuditLedgerProgressionGate,
    ) -> RepositoryReleaseAuditLedgerProgressionGateSummary:
        if gate.passed and gate.comparison.snapshots_identical:
            return (
                RepositoryReleaseAuditLedgerProgressionGateSummary(
                    outcome="ledger_unchanged_passed",
                    message=(
                        "Ledger progression gate passed with no "
                        "changes between snapshots."
                    ),
                    action_required=False,
                )
            )

        if gate.passed:
            return (
                RepositoryReleaseAuditLedgerProgressionGateSummary(
                    outcome="ledger_progression_passed",
                    message=(
                        f"Ledger progression gate passed with "
                        f"{len(gate.comparison.added_bundle_ids)} "
                        f"appended bundle record or records."
                    ),
                    action_required=False,
                )
            )

        if gate.critical_reason_count > 0:
            return (
                RepositoryReleaseAuditLedgerProgressionGateSummary(
                    outcome="ledger_progression_blocked_critical",
                    message=(
                        f"Ledger progression gate blocked with "
                        f"{gate.reason_count} reason(s), including "
                        f"{gate.critical_reason_count} critical."
                    ),
                    action_required=True,
                )
            )

        return RepositoryReleaseAuditLedgerProgressionGateSummary(
            outcome="ledger_progression_blocked",
            message=(
                f"Ledger progression gate blocked with "
                f"{gate.reason_count} reason(s)."
            ),
            action_required=True,
        )
