from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_architecture_report import (
    RepositoryArchitectureReportBuilder,
)
from app.connectors.repository.repository_knowledge_graph import (
    RepositoryKnowledgeGraphBuilder,
)
from app.connectors.repository.repository_search_index import (
    RepositorySearchIndexBuilder,
)
from app.connectors.repository.repository_summary import (
    RepositorySummaryBuilder,
)


@dataclass(frozen=True)
class RepositoryIntelligenceMetric:
    name: str
    value: int
    status: str
    description: str = ""


@dataclass(frozen=True)
class RepositoryIntelligenceDashboard:
    repository_path: str
    repository_name: str
    metrics: list[RepositoryIntelligenceMetric] = field(
        default_factory=list
    )
    warnings: list[str] = field(default_factory=list)

    @property
    def metric_count(self) -> int:
        return len(self.metrics)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    @property
    def healthy_metric_count(self) -> int:
        return sum(
            metric.status == "healthy"
            for metric in self.metrics
        )

    @property
    def warning_metric_count(self) -> int:
        return sum(
            metric.status == "warning"
            for metric in self.metrics
        )

    @property
    def critical_metric_count(self) -> int:
        return sum(
            metric.status == "critical"
            for metric in self.metrics
        )

    @property
    def is_healthy(self) -> bool:
        return (
            self.warning_count == 0
            and self.warning_metric_count == 0
            and self.critical_metric_count == 0
        )

    @property
    def metric_names(self) -> list[str]:
        return [metric.name for metric in self.metrics]

    def metric_value(self, name: str) -> int | None:
        for metric in self.metrics:
            if metric.name == name:
                return metric.value

        return None

    def metrics_by_status(
        self,
        status: str,
    ) -> list[RepositoryIntelligenceMetric]:
        return [
            metric
            for metric in self.metrics
            if metric.status == status
        ]


class RepositoryIntelligenceDashboardBuilder:
    def build(
        self,
        repository_path: str | Path,
        max_depth: int = 8,
    ) -> RepositoryIntelligenceDashboard:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(
                f"Repository path does not exist: {root}"
            )

        if not root.is_dir():
            raise NotADirectoryError(
                f"Repository path is not a directory: {root}"
            )

        graph = RepositoryKnowledgeGraphBuilder().build(
            root,
            max_depth=max_depth,
        )

        search_index = RepositorySearchIndexBuilder().build(
            root,
            max_depth=max_depth,
        )

        architecture = RepositoryArchitectureReportBuilder().build(
            root,
            max_depth=max_depth,
        )

        summary = RepositorySummaryBuilder().build(
            root,
            max_depth=max_depth,
        )

        metrics = [
            self._metric(
                name="knowledge_graph_nodes",
                value=graph.node_count,
                healthy=graph.node_count > 0,
                description="Total repository knowledge graph nodes.",
            ),
            self._metric(
                name="knowledge_graph_edges",
                value=graph.edge_count,
                healthy=graph.edge_count > 0,
                description="Total repository knowledge graph relationships.",
            ),
            self._metric(
                name="file_nodes",
                value=graph.file_node_count,
                healthy=graph.file_node_count > 0,
                description="Files represented in the knowledge graph.",
            ),
            self._metric(
                name="package_nodes",
                value=graph.package_node_count,
                healthy=graph.package_node_count > 0,
                description="Package markers represented in the graph.",
            ),
            self._metric(
                name="dependency_nodes",
                value=graph.dependency_node_count,
                healthy=graph.dependency_node_count > 0,
                description="Dependencies represented in the graph.",
            ),
            self._metric(
                name="import_nodes",
                value=graph.import_node_count,
                healthy=graph.import_node_count > 0,
                description="Imports represented in the graph.",
            ),
            self._metric(
                name="symbol_nodes",
                value=graph.symbol_node_count,
                healthy=graph.symbol_node_count > 0,
                description="Symbols represented in the graph.",
            ),
            self._metric(
                name="search_documents",
                value=search_index.document_count,
                healthy=search_index.document_count > 0,
                description="Documents available to repository search.",
            ),
            self._metric(
                name="architecture_findings",
                value=architecture.finding_count,
                healthy=architecture.finding_count > 0,
                description="Architecture observations generated.",
            ),
            self._metric(
                name="summary_sections",
                value=summary.section_count,
                healthy=summary.section_count > 0,
                description="Sections available in the repository summary.",
            ),
        ]

        warnings = []

        if architecture.warning_count > 0:
            warnings.append(
                f"architecture_warnings:{architecture.warning_count}"
            )

        if architecture.critical_count > 0:
            warnings.append(
                f"architecture_critical:{architecture.critical_count}"
            )

        for metric in metrics:
            if metric.status != "healthy":
                warnings.append(
                    f"metric_{metric.status}:{metric.name}"
                )

        return RepositoryIntelligenceDashboard(
            repository_path=str(root),
            repository_name=root.name,
            metrics=metrics,
            warnings=sorted(set(warnings)),
        )

    def _metric(
        self,
        name: str,
        value: int,
        healthy: bool,
        description: str,
    ) -> RepositoryIntelligenceMetric:
        return RepositoryIntelligenceMetric(
            name=name,
            value=value,
            status="healthy" if healthy else "warning",
            description=description,
        )
