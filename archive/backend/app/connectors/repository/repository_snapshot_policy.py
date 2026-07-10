from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshot,
    RepositoryIntelligenceSnapshotBuilder,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
)


@dataclass(frozen=True)
class RepositorySnapshotPolicy:
    require_fingerprint_match: bool = False
    allow_added_metrics: bool = True
    allow_removed_metrics: bool = False
    max_warning_delta: int = 0
    max_critical_delta: int = 0
    max_node_decrease: int = 0
    max_edge_decrease: int = 0
    max_metric_decrease: int = 0


@dataclass(frozen=True)
class RepositorySnapshotPolicyViolation:
    rule: str
    subject: str
    message: str
    severity: str = "error"


@dataclass(frozen=True)
class RepositorySnapshotPolicyEvaluation:
    repository_path: str
    baseline_fingerprint: str
    candidate_fingerprint: str
    policy: RepositorySnapshotPolicy
    violations: list[RepositorySnapshotPolicyViolation] = field(
        default_factory=list
    )

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    @property
    def passed(self) -> bool:
        return self.violation_count == 0

    @property
    def failed_rules(self) -> list[str]:
        return sorted(
            {
                violation.rule
                for violation in self.violations
            }
        )

    @property
    def critical_violation_count(self) -> int:
        return sum(
            violation.severity == "critical"
            for violation in self.violations
        )

    @property
    def error_violation_count(self) -> int:
        return sum(
            violation.severity == "error"
            for violation in self.violations
        )


class RepositorySnapshotPolicyEvaluator:
    def evaluate(
        self,
        repository_path: str | Path,
        baseline: RepositorySnapshotBaseline,
        policy: RepositorySnapshotPolicy,
        max_depth: int = 8,
    ) -> RepositorySnapshotPolicyEvaluation:
        candidate = RepositoryIntelligenceSnapshotBuilder().build(
            repository_path=repository_path,
            max_depth=max_depth,
        )

        return self.evaluate_snapshot(
            candidate=candidate,
            baseline=baseline,
            policy=policy,
        )

    def evaluate_snapshot(
        self,
        candidate: RepositoryIntelligenceSnapshot,
        baseline: RepositorySnapshotBaseline,
        policy: RepositorySnapshotPolicy,
    ) -> RepositorySnapshotPolicyEvaluation:
        violations: list[RepositorySnapshotPolicyViolation] = []

        if (
            policy.require_fingerprint_match
            and candidate.fingerprint != baseline.fingerprint
        ):
            violations.append(
                RepositorySnapshotPolicyViolation(
                    rule="require_fingerprint_match",
                    subject="fingerprint",
                    message=(
                        "Candidate fingerprint does not match "
                        "the baseline fingerprint."
                    ),
                    severity="critical",
                )
            )

        warning_delta = (
            candidate.warning_count
            - baseline.warning_count
        )

        if warning_delta > policy.max_warning_delta:
            violations.append(
                RepositorySnapshotPolicyViolation(
                    rule="max_warning_delta",
                    subject="warning_count",
                    message=(
                        f"Warning count increased by {warning_delta}; "
                        f"policy allows {policy.max_warning_delta}."
                    ),
                )
            )

        critical_delta = (
            candidate.critical_count
            - baseline.critical_count
        )

        if critical_delta > policy.max_critical_delta:
            violations.append(
                RepositorySnapshotPolicyViolation(
                    rule="max_critical_delta",
                    subject="critical_count",
                    message=(
                        f"Critical count increased by {critical_delta}; "
                        f"policy allows {policy.max_critical_delta}."
                    ),
                    severity="critical",
                )
            )

        node_decrease = max(
            0,
            baseline.node_count - candidate.node_count,
        )

        if node_decrease > policy.max_node_decrease:
            violations.append(
                RepositorySnapshotPolicyViolation(
                    rule="max_node_decrease",
                    subject="node_count",
                    message=(
                        f"Knowledge graph node count decreased by "
                        f"{node_decrease}; policy allows "
                        f"{policy.max_node_decrease}."
                    ),
                )
            )

        edge_decrease = max(
            0,
            baseline.edge_count - candidate.edge_count,
        )

        if edge_decrease > policy.max_edge_decrease:
            violations.append(
                RepositorySnapshotPolicyViolation(
                    rule="max_edge_decrease",
                    subject="edge_count",
                    message=(
                        f"Knowledge graph edge count decreased by "
                        f"{edge_decrease}; policy allows "
                        f"{policy.max_edge_decrease}."
                    ),
                )
            )

        baseline_metrics = {
            metric.name: metric.value
            for metric in baseline.metrics
        }

        candidate_metrics = {
            metric.name: metric.value
            for metric in candidate.metrics
        }

        added_metrics = sorted(
            set(candidate_metrics)
            - set(baseline_metrics)
        )

        if added_metrics and not policy.allow_added_metrics:
            for name in added_metrics:
                violations.append(
                    RepositorySnapshotPolicyViolation(
                        rule="allow_added_metrics",
                        subject=name,
                        message=(
                            f"Candidate added metric {name}, "
                            "but added metrics are not allowed."
                        ),
                    )
                )

        removed_metrics = sorted(
            set(baseline_metrics)
            - set(candidate_metrics)
        )

        if removed_metrics and not policy.allow_removed_metrics:
            for name in removed_metrics:
                violations.append(
                    RepositorySnapshotPolicyViolation(
                        rule="allow_removed_metrics",
                        subject=name,
                        message=(
                            f"Candidate removed metric {name}, "
                            "but removed metrics are not allowed."
                        ),
                        severity="critical",
                    )
                )

        for name in sorted(
            set(baseline_metrics)
            & set(candidate_metrics)
        ):
            decrease = max(
                0,
                baseline_metrics[name]
                - candidate_metrics[name],
            )

            if decrease > policy.max_metric_decrease:
                violations.append(
                    RepositorySnapshotPolicyViolation(
                        rule="max_metric_decrease",
                        subject=name,
                        message=(
                            f"Metric {name} decreased by {decrease}; "
                            f"policy allows "
                            f"{policy.max_metric_decrease}."
                        ),
                    )
                )

        return RepositorySnapshotPolicyEvaluation(
            repository_path=candidate.repository_path,
            baseline_fingerprint=baseline.fingerprint,
            candidate_fingerprint=candidate.fingerprint,
            policy=policy,
            violations=sorted(
                violations,
                key=lambda violation: (
                    violation.rule,
                    violation.subject,
                ),
            ),
        )
