from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_audit_ledger_snapshot_comparison import (
    RepositoryReleaseAuditLedgerSnapshotComparison,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerSnapshotComparisonSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseAuditLedgerSnapshotComparisonSummaryBuilder:
    def build(
        self,
        comparison: RepositoryReleaseAuditLedgerSnapshotComparison,
    ) -> RepositoryReleaseAuditLedgerSnapshotComparisonSummary:
        if comparison.snapshots_identical:
            return (
                RepositoryReleaseAuditLedgerSnapshotComparisonSummary(
                    outcome="ledger_snapshot_unchanged",
                    message=(
                        "Baseline and candidate ledger snapshots "
                        "are identical."
                    ),
                    action_required=False,
                )
            )

        if comparison.history_rewritten:
            return (
                RepositoryReleaseAuditLedgerSnapshotComparisonSummary(
                    outcome="ledger_history_rewritten",
                    message=(
                        "Candidate ledger snapshot does not preserve "
                        "the baseline entry history."
                    ),
                    action_required=True,
                )
            )

        if comparison.acceptance_regression:
            return (
                RepositoryReleaseAuditLedgerSnapshotComparisonSummary(
                    outcome="ledger_acceptance_regression",
                    message=(
                        "Candidate ledger snapshot regressed from "
                        "accepted to unaccepted."
                    ),
                    action_required=True,
                )
            )

        if comparison.safe_progression:
            return (
                RepositoryReleaseAuditLedgerSnapshotComparisonSummary(
                    outcome="ledger_safe_progression",
                    message=(
                        f"Candidate ledger safely appended "
                        f"{len(comparison.added_bundle_ids)} bundle "
                        f"record or records."
                    ),
                    action_required=False,
                )
            )

        return RepositoryReleaseAuditLedgerSnapshotComparisonSummary(
            outcome="ledger_snapshot_changed",
            message=(
                f"Ledger snapshot changed with entry-count delta "
                f"{comparison.entry_count_delta}."
            ),
            action_required=True,
        )
