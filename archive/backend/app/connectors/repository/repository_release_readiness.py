from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_intelligence_dashboard import (
    RepositoryIntelligenceDashboard,
    RepositoryIntelligenceDashboardBuilder,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
)
from app.connectors.repository.repository_snapshot_gate import (
    RepositorySnapshotGateEvaluator,
    RepositorySnapshotGateResult,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)


@dataclass(frozen=True)
class RepositoryReleaseReadinessCheck:
    name: str
    passed: bool
    severity: str
    message: str


@dataclass(frozen=True)
class RepositoryReleaseReadiness:
    repository_path: str
    repository_name: str
    gate: RepositorySnapshotGateResult
    dashboard: RepositoryIntelligenceDashboard
    checks: list[RepositoryReleaseReadinessCheck] = field(
        default_factory=list
    )

    @property
    def check_count(self) -> int:
        return len(self.checks)

    @property
    def passed_check_count(self) -> int:
        return sum(check.passed for check in self.checks)

    @property
    def failed_check_count(self) -> int:
        return sum(not check.passed for check in self.checks)

    @property
    def critical_failure_count(self) -> int:
        return sum(
            not check.passed and check.severity == "critical"
            for check in self.checks
        )

    @property
    def warning_failure_count(self) -> int:
        return sum(
            not check.passed and check.severity == "warning"
            for check in self.checks
        )

    @property
    def failed_check_names(self) -> list[str]:
        return [
            check.name
            for check in self.checks
            if not check.passed
        ]

    @property
    def release_ready(self) -> bool:
        return (
            self.gate.passed
            and self.dashboard.is_healthy
            and self.failed_check_count == 0
        )

    @property
    def blocked(self) -> bool:
        return not self.release_ready

    @property
    def exit_code(self) -> int:
        return 0 if self.release_ready else 1

    @property
    def status(self) -> str:
        if self.release_ready:
            return "release_ready"

        if self.critical_failure_count > 0:
            return "blocked_critical"

        return "blocked"


class RepositoryReleaseReadinessEvaluator:
    def evaluate(
        self,
        repository_path: str | Path,
        baseline: RepositorySnapshotBaseline,
        policy: RepositorySnapshotPolicy,
        max_depth: int = 8,
    ) -> RepositoryReleaseReadiness:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(
                f"Repository path does not exist: {root}"
            )

        if not root.is_dir():
            raise NotADirectoryError(
                f"Repository path is not a directory: {root}"
            )

        gate = RepositorySnapshotGateEvaluator().evaluate(
            repository_path=root,
            baseline=baseline,
            policy=policy,
            max_depth=max_depth,
        )

        dashboard = RepositoryIntelligenceDashboardBuilder().build(
            repository_path=root,
            max_depth=max_depth,
        )

        checks = [
            RepositoryReleaseReadinessCheck(
                name="snapshot_gate",
                passed=gate.passed,
                severity="critical",
                message=(
                    "Repository snapshot gate passed."
                    if gate.passed
                    else (
                        "Repository snapshot gate failed with "
                        f"{gate.reason_count} reason(s)."
                    )
                ),
            ),
            RepositoryReleaseReadinessCheck(
                name="intelligence_dashboard",
                passed=dashboard.is_healthy,
                severity="critical",
                message=(
                    "Repository intelligence dashboard is healthy."
                    if dashboard.is_healthy
                    else (
                        "Repository intelligence dashboard contains "
                        f"{dashboard.warning_count} warning(s)."
                    )
                ),
            ),
            RepositoryReleaseReadinessCheck(
                name="knowledge_graph",
                passed=(
                    (dashboard.metric_value("knowledge_graph_nodes") or 0)
                    > 0
                ),
                severity="critical",
                message="Repository knowledge graph contains nodes.",
            ),
            RepositoryReleaseReadinessCheck(
                name="search_index",
                passed=(
                    (dashboard.metric_value("search_documents") or 0)
                    > 0
                ),
                severity="warning",
                message="Repository search index contains documents.",
            ),
            RepositoryReleaseReadinessCheck(
                name="architecture_report",
                passed=(
                    (dashboard.metric_value("architecture_findings") or 0)
                    > 0
                ),
                severity="warning",
                message="Repository architecture findings are available.",
            ),
            RepositoryReleaseReadinessCheck(
                name="repository_summary",
                passed=(
                    (dashboard.metric_value("summary_sections") or 0)
                    > 0
                ),
                severity="warning",
                message="Repository summary sections are available.",
            ),
        ]

        return RepositoryReleaseReadiness(
            repository_path=str(root),
            repository_name=root.name,
            gate=gate,
            dashboard=dashboard,
            checks=checks,
        )
