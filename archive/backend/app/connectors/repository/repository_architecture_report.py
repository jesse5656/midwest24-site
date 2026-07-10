from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_knowledge_graph import RepositoryKnowledgeGraphBuilder
from app.connectors.repository.repository_summary import RepositorySummaryBuilder


@dataclass(frozen=True)
class RepositoryArchitectureFinding:
    name: str
    severity: str
    message: str


@dataclass(frozen=True)
class RepositoryArchitectureReport:
    repository_path: str
    title: str
    findings: list[RepositoryArchitectureFinding] = field(default_factory=list)

    @property
    def finding_count(self) -> int:
        return len(self.findings)

    @property
    def severity_levels(self) -> list[str]:
        return sorted({finding.severity for finding in self.findings})

    @property
    def info_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "info")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def critical_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "critical")

    @property
    def has_warnings(self) -> bool:
        return self.warning_count > 0 or self.critical_count > 0

    def findings_by_severity(self, severity: str) -> list[RepositoryArchitectureFinding]:
        return [finding for finding in self.findings if finding.severity == severity]


class RepositoryArchitectureReportBuilder:
    def build(self, repository_path: str | Path, max_depth: int = 8) -> RepositoryArchitectureReport:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")

        graph = RepositoryKnowledgeGraphBuilder().build(root, max_depth=max_depth)
        summary = RepositorySummaryBuilder().build(root, max_depth=max_depth)

        findings = [
            RepositoryArchitectureFinding(
                name="repository_summary_available",
                severity="info",
                message=f"Repository summary contains {summary.section_count} section(s).",
            ),
            RepositoryArchitectureFinding(
                name="knowledge_graph_available",
                severity="info",
                message=f"Knowledge graph contains {graph.node_count} node(s) and {graph.edge_count} edge(s).",
            ),
            RepositoryArchitectureFinding(
                name="file_inventory_available",
                severity="info",
                message=f"Repository contains {graph.file_node_count} file node(s).",
            ),
            RepositoryArchitectureFinding(
                name="symbol_inventory_available",
                severity="info" if graph.symbol_node_count > 0 else "warning",
                message=f"Repository contains {graph.symbol_node_count} symbol node(s).",
            ),
            RepositoryArchitectureFinding(
                name="dependency_inventory_available",
                severity="info" if graph.dependency_node_count > 0 else "warning",
                message=f"Repository contains {graph.dependency_node_count} dependency node(s).",
            ),
            RepositoryArchitectureFinding(
                name="import_inventory_available",
                severity="info" if graph.import_node_count > 0 else "warning",
                message=f"Repository contains {graph.import_node_count} import node(s).",
            ),
        ]

        return RepositoryArchitectureReport(
            repository_path=str(root),
            title=f"{root.name} Architecture Report",
            findings=findings,
        )
