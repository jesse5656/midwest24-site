from __future__ import annotations

from dataclasses import dataclass, field

from app.connectors.repository.repository_release_audit_ledger_snapshot_comparison import (
    RepositoryReleaseAuditLedgerSnapshotComparison,
    RepositoryReleaseAuditLedgerSnapshotComparisonBuilder,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerProgressionGateReason:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerProgressionGate:
    comparison: RepositoryReleaseAuditLedgerSnapshotComparison
    allow_unchanged: bool = True
    require_candidate_accepted: bool = True
    reasons: list[
        RepositoryReleaseAuditLedgerProgressionGateReason
    ] = field(default_factory=list)

    @property
    def reason_count(self) -> int:
        return len(self.reasons)

    @property
    def critical_reason_count(self) -> int:
        return sum(
            reason.severity == "critical"
            for reason in self.reasons
        )

    @property
    def error_reason_count(self) -> int:
        return sum(
            reason.severity == "error"
            for reason in self.reasons
        )

    @property
    def warning_reason_count(self) -> int:
        return sum(
            reason.severity == "warning"
            for reason in self.reasons
        )

    @property
    def reason_codes(self) -> list[str]:
        return sorted(
            {
                reason.code
                for reason in self.reasons
            }
        )

    @property
    def passed(self) -> bool:
        return (
            self.critical_reason_count == 0
            and self.error_reason_count == 0
        )

    @property
    def blocked(self) -> bool:
        return not self.passed

    @property
    def exit_code(self) -> int:
        return 0 if self.passed else 1

    @property
    def status(self) -> str:
        if self.passed and self.comparison.snapshots_identical:
            return "unchanged_passed"

        if self.passed:
            return "progression_passed"

        if self.critical_reason_count > 0:
            return "progression_blocked_critical"

        return "progression_blocked"


class RepositoryReleaseAuditLedgerProgressionGateEvaluator:
    def evaluate(
        self,
        baseline_snapshot_json: str,
        candidate_snapshot_json: str,
        allow_unchanged: bool = True,
        require_candidate_accepted: bool = True,
    ) -> RepositoryReleaseAuditLedgerProgressionGate:
        comparison = (
            RepositoryReleaseAuditLedgerSnapshotComparisonBuilder()
            .build(
                baseline_snapshot_json=baseline_snapshot_json,
                candidate_snapshot_json=candidate_snapshot_json,
                require_accepted=False,
            )
        )

        return self.from_comparison(
            comparison=comparison,
            allow_unchanged=allow_unchanged,
            require_candidate_accepted=(
                require_candidate_accepted
            ),
        )

    def from_comparison(
        self,
        comparison: RepositoryReleaseAuditLedgerSnapshotComparison,
        allow_unchanged: bool = True,
        require_candidate_accepted: bool = True,
    ) -> RepositoryReleaseAuditLedgerProgressionGate:
        reasons: list[
            RepositoryReleaseAuditLedgerProgressionGateReason
        ] = []

        if not comparison.baseline_verification.valid:
            reasons.append(
                RepositoryReleaseAuditLedgerProgressionGateReason(
                    code="baseline_snapshot_invalid",
                    severity="critical",
                    message=(
                        "Baseline ledger snapshot failed "
                        "verification."
                    ),
                )
            )

        if not comparison.candidate_verification.valid:
            reasons.append(
                RepositoryReleaseAuditLedgerProgressionGateReason(
                    code="candidate_snapshot_invalid",
                    severity="critical",
                    message=(
                        "Candidate ledger snapshot failed "
                        "verification."
                    ),
                )
            )

        if (
            require_candidate_accepted
            and not comparison.candidate_verification.accepted
        ):
            reasons.append(
                RepositoryReleaseAuditLedgerProgressionGateReason(
                    code="candidate_snapshot_not_accepted",
                    severity="error",
                    message=(
                        "Candidate ledger snapshot is not accepted."
                    ),
                )
            )

        if (
            comparison.snapshots_identical
            and not allow_unchanged
        ):
            reasons.append(
                RepositoryReleaseAuditLedgerProgressionGateReason(
                    code="unchanged_snapshot_not_allowed",
                    severity="error",
                    message=(
                        "Candidate snapshot is unchanged, but "
                        "this gate requires a progression."
                    ),
                )
            )

        if comparison.history_rewritten:
            reasons.append(
                RepositoryReleaseAuditLedgerProgressionGateReason(
                    code="ledger_history_rewritten",
                    severity="critical",
                    message=(
                        "Candidate ledger does not preserve the "
                        "baseline ledger history."
                    ),
                )
            )

        if comparison.removed_bundle_ids:
            reasons.append(
                RepositoryReleaseAuditLedgerProgressionGateReason(
                    code="ledger_bundles_removed",
                    severity="critical",
                    message=(
                        f"Candidate ledger removed "
                        f"{len(comparison.removed_bundle_ids)} "
                        f"bundle record or records."
                    ),
                )
            )

        if comparison.acceptance_regression:
            reasons.append(
                RepositoryReleaseAuditLedgerProgressionGateReason(
                    code="ledger_acceptance_regression",
                    severity="critical",
                    message=(
                        "Candidate ledger regressed from accepted "
                        "to unaccepted."
                    ),
                )
            )

        if (
            not comparison.snapshots_identical
            and not comparison.safe_progression
            and not comparison.history_rewritten
            and not comparison.acceptance_regression
        ):
            reasons.append(
                RepositoryReleaseAuditLedgerProgressionGateReason(
                    code="unsafe_ledger_progression",
                    severity="error",
                    message=(
                        "Candidate ledger changed without meeting "
                        "safe progression requirements."
                    ),
                )
            )

        deduplicated = {
            (
                reason.code,
                reason.severity,
                reason.message,
            ): reason
            for reason in reasons
        }

        ordered = sorted(
            deduplicated.values(),
            key=lambda reason: (
                0 if reason.severity == "critical" else 1,
                reason.code,
                reason.message,
            ),
        )

        return RepositoryReleaseAuditLedgerProgressionGate(
            comparison=comparison,
            allow_unchanged=allow_unchanged,
            require_candidate_accepted=(
                require_candidate_accepted
            ),
            reasons=ordered,
        )
