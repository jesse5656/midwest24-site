from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
    RepositorySnapshotBaselineVerification,
    RepositorySnapshotBaselineVerifier,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
    RepositorySnapshotPolicyEvaluation,
    RepositorySnapshotPolicyEvaluator,
)


@dataclass(frozen=True)
class RepositorySnapshotGateReason:
    code: str
    message: str
    severity: str


@dataclass(frozen=True)
class RepositorySnapshotGateResult:
    repository_path: str
    baseline_verification: RepositorySnapshotBaselineVerification
    policy_evaluation: RepositorySnapshotPolicyEvaluation
    reasons: list[RepositorySnapshotGateReason] = field(
        default_factory=list
    )

    @property
    def passed(self) -> bool:
        return (
            self.baseline_verification.matches
            and self.policy_evaluation.passed
            and not self.reasons
        )

    @property
    def blocked(self) -> bool:
        return not self.passed

    @property
    def exit_code(self) -> int:
        return 0 if self.passed else 1

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
    def status(self) -> str:
        if self.passed:
            return "passed"

        if self.critical_reason_count > 0:
            return "blocked_critical"

        return "blocked"


class RepositorySnapshotGateEvaluator:
    def evaluate(
        self,
        repository_path: str | Path,
        baseline: RepositorySnapshotBaseline,
        policy: RepositorySnapshotPolicy,
        max_depth: int = 8,
    ) -> RepositorySnapshotGateResult:
        verification = RepositorySnapshotBaselineVerifier().verify(
            repository_path=repository_path,
            baseline=baseline,
            max_depth=max_depth,
        )

        policy_evaluation = RepositorySnapshotPolicyEvaluator().evaluate(
            repository_path=repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=max_depth,
        )

        return self.evaluate_results(
            repository_path=str(repository_path),
            verification=verification,
            policy_evaluation=policy_evaluation,
        )

    def evaluate_results(
        self,
        repository_path: str,
        verification: RepositorySnapshotBaselineVerification,
        policy_evaluation: RepositorySnapshotPolicyEvaluation,
    ) -> RepositorySnapshotGateResult:
        reasons: list[RepositorySnapshotGateReason] = []

        if not verification.fingerprint_matches:
            reasons.append(
                RepositorySnapshotGateReason(
                    code="baseline_fingerprint_mismatch",
                    message=(
                        "Candidate repository fingerprint does not "
                        "match the baseline fingerprint."
                    ),
                    severity="warning",
                )
            )

        for difference in verification.metric_differences:
            reasons.append(
                RepositorySnapshotGateReason(
                    code="baseline_difference",
                    message=difference,
                    severity="warning",
                )
            )

        for violation in policy_evaluation.violations:
            reasons.append(
                RepositorySnapshotGateReason(
                    code=f"policy:{violation.rule}",
                    message=violation.message,
                    severity=(
                        "critical"
                        if violation.severity == "critical"
                        else "warning"
                    ),
                )
            )

        deduplicated = {
            (
                reason.code,
                reason.message,
                reason.severity,
            ): reason
            for reason in reasons
        }

        ordered_reasons = sorted(
            deduplicated.values(),
            key=lambda reason: (
                0 if reason.severity == "critical" else 1,
                reason.code,
                reason.message,
            ),
        )

        return RepositorySnapshotGateResult(
            repository_path=repository_path,
            baseline_verification=verification,
            policy_evaluation=policy_evaluation,
            reasons=ordered_reasons,
        )
