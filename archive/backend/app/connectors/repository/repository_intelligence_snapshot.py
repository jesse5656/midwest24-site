from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.connectors.repository.repository_intelligence_dashboard import (
    RepositoryIntelligenceDashboardBuilder,
)
from app.connectors.repository.repository_intelligence_report import (
    RepositoryIntelligenceReportBuilder,
)
from app.connectors.repository.repository_knowledge_graph import (
    RepositoryKnowledgeGraphBuilder,
)


@dataclass(frozen=True)
class RepositoryIntelligenceSnapshotMetric:
    name: str
    value: int
    status: str


@dataclass(frozen=True)
class RepositoryIntelligenceSnapshot:
    repository_path: str
    repository_name: str
    metrics: list[RepositoryIntelligenceSnapshotMetric] = field(
        default_factory=list
    )
    node_count: int = 0
    edge_count: int = 0
    report_section_count: int = 0
    warning_count: int = 0
    critical_count: int = 0
    fingerprint: str = ""

    @property
    def metric_count(self) -> int:
        return len(self.metrics)

    @property
    def is_healthy(self) -> bool:
        return (
            self.warning_count == 0
            and self.critical_count == 0
        )

    @property
    def metric_names(self) -> list[str]:
        return [metric.name for metric in self.metrics]

    def metric_value(self, name: str) -> int | None:
        for metric in self.metrics:
            if metric.name == name:
                return metric.value

        return None

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "repository_name": self.repository_name,
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

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        )


class RepositoryIntelligenceSnapshotBuilder:
    def build(
        self,
        repository_path: str | Path,
        max_depth: int = 8,
    ) -> RepositoryIntelligenceSnapshot:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(
                f"Repository path does not exist: {root}"
            )

        if not root.is_dir():
            raise NotADirectoryError(
                f"Repository path is not a directory: {root}"
            )

        dashboard = RepositoryIntelligenceDashboardBuilder().build(
            repository_path=root,
            max_depth=max_depth,
        )

        report = RepositoryIntelligenceReportBuilder().build(
            repository_path=root,
            max_depth=max_depth,
        )

        graph = RepositoryKnowledgeGraphBuilder().build(
            repository_path=root,
            max_depth=max_depth,
        )

        metrics = [
            RepositoryIntelligenceSnapshotMetric(
                name=metric.name,
                value=metric.value,
                status=metric.status,
            )
            for metric in sorted(
                dashboard.metrics,
                key=lambda item: item.name,
            )
        ]

        provisional = RepositoryIntelligenceSnapshot(
            repository_path=str(root),
            repository_name=root.name,
            metrics=metrics,
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            report_section_count=report.section_count,
            warning_count=report.warning_count,
            critical_count=report.critical_count,
        )

        fingerprint = hashlib.sha256(
            provisional.canonical_json().encode("utf-8")
        ).hexdigest()

        return RepositoryIntelligenceSnapshot(
            repository_path=provisional.repository_path,
            repository_name=provisional.repository_name,
            metrics=provisional.metrics,
            node_count=provisional.node_count,
            edge_count=provisional.edge_count,
            report_section_count=provisional.report_section_count,
            warning_count=provisional.warning_count,
            critical_count=provisional.critical_count,
            fingerprint=fingerprint,
        )
