from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshot,
    RepositoryIntelligenceSnapshotBuilder,
)


@dataclass(frozen=True)
class RepositorySnapshotMetricChange:
    name: str
    baseline_value: int | None
    candidate_value: int | None
    delta: int | None
    change_type: str


@dataclass(frozen=True)
class RepositorySnapshotComparison:
    baseline_repository_path: str
    candidate_repository_path: str
    baseline_fingerprint: str
    candidate_fingerprint: str
    metric_changes: list[RepositorySnapshotMetricChange] = field(
        default_factory=list
    )
    node_delta: int = 0
    edge_delta: int = 0
    report_section_delta: int = 0
    warning_delta: int = 0
    critical_delta: int = 0

    @property
    def fingerprints_match(self) -> bool:
        return (
            self.baseline_fingerprint
            == self.candidate_fingerprint
        )

    
    @property
    def has_changes(self) -> bool:
        if not self.fingerprints_match:
            return True

        if (
            self.node_delta != 0
            or self.edge_delta != 0
            or self.report_section_delta != 0
            or self.warning_delta != 0
            or self.critical_delta != 0
        ):
            return True

        return any(
            change.change_type != "unchanged"
            for change in self.metric_changes
        )

    @property
    def metric_change_count(self) -> int:
        return len(self.metric_changes)

    @property
    def increased_metric_count(self) -> int:
        return sum(
            change.change_type == "increased"
            for change in self.metric_changes
        )

    @property
    def decreased_metric_count(self) -> int:
        return sum(
            change.change_type == "decreased"
            for change in self.metric_changes
        )

    @property
    def added_metric_count(self) -> int:
        return sum(
            change.change_type == "added"
            for change in self.metric_changes
        )

    @property
    def removed_metric_count(self) -> int:
        return sum(
            change.change_type == "removed"
            for change in self.metric_changes
        )

    @property
    def unchanged_metric_count(self) -> int:
        return sum(
            change.change_type == "unchanged"
            for change in self.metric_changes
        )

    @property
    def changed_metric_names(self) -> list[str]:
        return [
            change.name
            for change in self.metric_changes
            if change.change_type != "unchanged"
        ]


class RepositorySnapshotComparisonBuilder:
    def compare(
        self,
        baseline_repository_path: str | Path,
        candidate_repository_path: str | Path,
        max_depth: int = 8,
    ) -> RepositorySnapshotComparison:
        baseline = RepositoryIntelligenceSnapshotBuilder().build(
            repository_path=baseline_repository_path,
            max_depth=max_depth,
        )

        candidate = RepositoryIntelligenceSnapshotBuilder().build(
            repository_path=candidate_repository_path,
            max_depth=max_depth,
        )

        return self.compare_snapshots(
            baseline=baseline,
            candidate=candidate,
        )

    def compare_snapshots(
        self,
        baseline: RepositoryIntelligenceSnapshot,
        candidate: RepositoryIntelligenceSnapshot,
    ) -> RepositorySnapshotComparison:
        baseline_metrics = {
            metric.name: metric.value
            for metric in baseline.metrics
        }

        candidate_metrics = {
            metric.name: metric.value
            for metric in candidate.metrics
        }

        metric_names = sorted(
            set(baseline_metrics)
            | set(candidate_metrics)
        )

        metric_changes = [
            self._compare_metric(
                name=name,
                baseline_value=baseline_metrics.get(name),
                candidate_value=candidate_metrics.get(name),
            )
            for name in metric_names
        ]

        return RepositorySnapshotComparison(
            baseline_repository_path=baseline.repository_path,
            candidate_repository_path=candidate.repository_path,
            baseline_fingerprint=baseline.fingerprint,
            candidate_fingerprint=candidate.fingerprint,
            metric_changes=metric_changes,
            node_delta=(
                candidate.node_count
                - baseline.node_count
            ),
            edge_delta=(
                candidate.edge_count
                - baseline.edge_count
            ),
            report_section_delta=(
                candidate.report_section_count
                - baseline.report_section_count
            ),
            warning_delta=(
                candidate.warning_count
                - baseline.warning_count
            ),
            critical_delta=(
                candidate.critical_count
                - baseline.critical_count
            ),
        )

    def _compare_metric(
        self,
        name: str,
        baseline_value: int | None,
        candidate_value: int | None,
    ) -> RepositorySnapshotMetricChange:
        if baseline_value is None:
            return RepositorySnapshotMetricChange(
                name=name,
                baseline_value=None,
                candidate_value=candidate_value,
                delta=None,
                change_type="added",
            )

        if candidate_value is None:
            return RepositorySnapshotMetricChange(
                name=name,
                baseline_value=baseline_value,
                candidate_value=None,
                delta=None,
                change_type="removed",
            )

        delta = candidate_value - baseline_value

        if delta > 0:
            change_type = "increased"
        elif delta < 0:
            change_type = "decreased"
        else:
            change_type = "unchanged"

        return RepositorySnapshotMetricChange(
            name=name,
            baseline_value=baseline_value,
            candidate_value=candidate_value,
            delta=delta,
            change_type=change_type,
        )
