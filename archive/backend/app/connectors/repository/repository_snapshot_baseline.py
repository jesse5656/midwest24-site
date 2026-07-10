from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.connectors.repository.repository_intelligence_snapshot import (
    RepositoryIntelligenceSnapshot,
    RepositoryIntelligenceSnapshotBuilder,
    RepositoryIntelligenceSnapshotMetric,
)


BASELINE_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class RepositorySnapshotBaselineMetric:
    name: str
    value: int
    status: str


@dataclass(frozen=True)
class RepositorySnapshotBaseline:
    schema_version: str
    repository_name: str
    fingerprint: str
    metrics: list[RepositorySnapshotBaselineMetric] = field(
        default_factory=list
    )
    node_count: int = 0
    edge_count: int = 0
    report_section_count: int = 0
    warning_count: int = 0
    critical_count: int = 0

    @property
    def metric_count(self) -> int:
        return len(self.metrics)

    @property
    def metric_names(self) -> list[str]:
        return [metric.name for metric in self.metrics]

    @property
    def is_healthy(self) -> bool:
        return (
            self.warning_count == 0
            and self.critical_count == 0
        )

    def metric_value(self, name: str) -> int | None:
        for metric in self.metrics:
            if metric.name == name:
                return metric.value
        return None

    def payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "repository_name": self.repository_name,
            "fingerprint": self.fingerprint,
            "metrics": [
                {
                    "name": metric.name,
                    "value": metric.value,
                    "status": metric.status,
                }
                for metric in sorted(
                    self.metrics,
                    key=lambda item: item.name,
                )
            ],
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "report_section_count": self.report_section_count,
            "warning_count": self.warning_count,
            "critical_count": self.critical_count,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.payload(),
            indent=2,
            sort_keys=True,
        ) + "\n"

    @classmethod
    def from_payload(
        cls,
        payload: dict[str, Any],
    ) -> RepositorySnapshotBaseline:
        return cls(
            schema_version=str(payload["schema_version"]),
            repository_name=str(payload["repository_name"]),
            fingerprint=str(payload["fingerprint"]),
            metrics=[
                RepositorySnapshotBaselineMetric(
                    name=str(metric["name"]),
                    value=int(metric["value"]),
                    status=str(metric["status"]),
                )
                for metric in payload.get("metrics", [])
            ],
            node_count=int(payload.get("node_count", 0)),
            edge_count=int(payload.get("edge_count", 0)),
            report_section_count=int(
                payload.get("report_section_count", 0)
            ),
            warning_count=int(payload.get("warning_count", 0)),
            critical_count=int(payload.get("critical_count", 0)),
        )

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> RepositorySnapshotBaseline:
        payload = json.loads(value)

        if not isinstance(payload, dict):
            raise ValueError(
                "Repository snapshot baseline JSON must contain an object."
            )

        required = {
            "schema_version",
            "repository_name",
            "fingerprint",
        }

        missing = sorted(required - set(payload))

        if missing:
            raise ValueError(
                "Repository snapshot baseline is missing required field(s): "
                + ", ".join(missing)
            )

        return cls.from_payload(payload)


@dataclass(frozen=True)
class RepositorySnapshotBaselineVerification:
    baseline: RepositorySnapshotBaseline
    candidate: RepositoryIntelligenceSnapshot
    fingerprint_matches: bool
    metric_differences: list[str] = field(default_factory=list)

    @property
    def matches(self) -> bool:
        return (
            self.fingerprint_matches
            and not self.metric_differences
        )

    @property
    def difference_count(self) -> int:
        return len(self.metric_differences)


class RepositorySnapshotBaselineBuilder:
    def build(
        self,
        repository_path: str | Path,
        max_depth: int = 8,
    ) -> RepositorySnapshotBaseline:
        snapshot = RepositoryIntelligenceSnapshotBuilder().build(
            repository_path=repository_path,
            max_depth=max_depth,
        )

        return self.from_snapshot(snapshot)

    def from_snapshot(
        self,
        snapshot: RepositoryIntelligenceSnapshot,
    ) -> RepositorySnapshotBaseline:
        return RepositorySnapshotBaseline(
            schema_version=BASELINE_SCHEMA_VERSION,
            repository_name=snapshot.repository_name,
            fingerprint=snapshot.fingerprint,
            metrics=[
                RepositorySnapshotBaselineMetric(
                    name=metric.name,
                    value=metric.value,
                    status=metric.status,
                )
                for metric in sorted(
                    snapshot.metrics,
                    key=lambda item: item.name,
                )
            ],
            node_count=snapshot.node_count,
            edge_count=snapshot.edge_count,
            report_section_count=snapshot.report_section_count,
            warning_count=snapshot.warning_count,
            critical_count=snapshot.critical_count,
        )


class RepositorySnapshotBaselineVerifier:
    def verify(
        self,
        repository_path: str | Path,
        baseline: RepositorySnapshotBaseline,
        max_depth: int = 8,
    ) -> RepositorySnapshotBaselineVerification:
        candidate = RepositoryIntelligenceSnapshotBuilder().build(
            repository_path=repository_path,
            max_depth=max_depth,
        )

        return self.verify_snapshot(
            candidate=candidate,
            baseline=baseline,
        )

    def verify_snapshot(
        self,
        candidate: RepositoryIntelligenceSnapshot,
        baseline: RepositorySnapshotBaseline,
    ) -> RepositorySnapshotBaselineVerification:
        differences: list[str] = []

        baseline_metrics = {
            metric.name: (
                metric.value,
                metric.status,
            )
            for metric in baseline.metrics
        }

        candidate_metrics = {
            metric.name: (
                metric.value,
                metric.status,
            )
            for metric in candidate.metrics
        }

        for name in sorted(
            set(baseline_metrics)
            | set(candidate_metrics)
        ):
            if name not in baseline_metrics:
                differences.append(
                    f"metric_added:{name}"
                )
                continue

            if name not in candidate_metrics:
                differences.append(
                    f"metric_removed:{name}"
                )
                continue

            if baseline_metrics[name] != candidate_metrics[name]:
                differences.append(
                    f"metric_changed:{name}"
                )

        scalar_values = {
            "node_count": (
                baseline.node_count,
                candidate.node_count,
            ),
            "edge_count": (
                baseline.edge_count,
                candidate.edge_count,
            ),
            "report_section_count": (
                baseline.report_section_count,
                candidate.report_section_count,
            ),
            "warning_count": (
                baseline.warning_count,
                candidate.warning_count,
            ),
            "critical_count": (
                baseline.critical_count,
                candidate.critical_count,
            ),
        }

        for name, values in scalar_values.items():
            if values[0] != values[1]:
                differences.append(
                    f"value_changed:{name}"
                )

        return RepositorySnapshotBaselineVerification(
            baseline=baseline,
            candidate=candidate,
            fingerprint_matches=(
                baseline.fingerprint
                == candidate.fingerprint
            ),
            metric_differences=sorted(set(differences)),
        )


def baseline_checksum(
    baseline: RepositorySnapshotBaseline,
) -> str:
    return hashlib.sha256(
        baseline.to_json().encode("utf-8")
    ).hexdigest()
