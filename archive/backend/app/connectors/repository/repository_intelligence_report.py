from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_architecture_report import (
    RepositoryArchitectureReportBuilder,
)
from app.connectors.repository.repository_intelligence_dashboard import (
    RepositoryIntelligenceDashboardBuilder,
)
from app.connectors.repository.repository_summary import (
    RepositorySummaryBuilder,
)


@dataclass(frozen=True)
class RepositoryIntelligenceReportSection:
    name: str
    content: str
    status: str = "info"


@dataclass(frozen=True)
class RepositoryIntelligenceReport:
    repository_path: str
    repository_name: str
    title: str
    sections: list[RepositoryIntelligenceReportSection] = field(
        default_factory=list
    )

    @property
    def section_count(self) -> int:
        return len(self.sections)

    @property
    def section_names(self) -> list[str]:
        return [section.name for section in self.sections]

    @property
    def info_count(self) -> int:
        return sum(
            section.status == "info"
            for section in self.sections
        )

    @property
    def warning_count(self) -> int:
        return sum(
            section.status == "warning"
            for section in self.sections
        )

    @property
    def critical_count(self) -> int:
        return sum(
            section.status == "critical"
            for section in self.sections
        )

    @property
    def is_healthy(self) -> bool:
        return (
            self.warning_count == 0
            and self.critical_count == 0
        )

    def section_content(
        self,
        name: str,
    ) -> str | None:
        for section in self.sections:
            if section.name == name:
                return section.content
        return None

    def sections_by_status(
        self,
        status: str,
    ) -> list[RepositoryIntelligenceReportSection]:
        return [
            section
            for section in self.sections
            if section.status == status
        ]

    def as_markdown(self) -> str:
        lines = [
            f"# {self.title}",
            "",
            f"Repository: `{self.repository_path}`",
            "",
        ]

        for section in self.sections:
            lines.extend(
                [
                    f"## {section.name}",
                    "",
                    section.content,
                    "",
                ]
            )

        return "\n".join(lines).rstrip() + "\n"


class RepositoryIntelligenceReportBuilder:
    def build(
        self,
        repository_path: str | Path,
        max_depth: int = 8,
    ) -> RepositoryIntelligenceReport:
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

        repository_summary = RepositorySummaryBuilder().build(
            repository_path=root,
            max_depth=max_depth,
        )

        architecture = RepositoryArchitectureReportBuilder().build(
            repository_path=root,
            max_depth=max_depth,
        )

        metric_lines = [
            (
                f"- **{metric.name}:** {metric.value} "
                f"({metric.status}) — {metric.description}"
            )
            for metric in dashboard.metrics
        ]

        summary_lines = [
            f"- **{section.name}:** {section.value}"
            for section in repository_summary.sections
        ]

        architecture_lines = [
            (
                f"- **{finding.name}:** {finding.message} "
                f"({finding.severity})"
            )
            for finding in architecture.findings
        ]

        warning_lines = (
            [f"- {warning}" for warning in dashboard.warnings]
            if dashboard.warnings
            else ["- No dashboard warnings detected."]
        )

        sections = [
            RepositoryIntelligenceReportSection(
                name="Executive Summary",
                content=(
                    f"{root.name} currently exposes "
                    f"{dashboard.metric_count} intelligence metrics. "
                    f"Overall dashboard status: "
                    f"{'healthy' if dashboard.is_healthy else 'attention required'}."
                ),
                status=(
                    "info"
                    if dashboard.is_healthy
                    else "warning"
                ),
            ),
            RepositoryIntelligenceReportSection(
                name="Repository Metrics",
                content="\n".join(metric_lines),
                status=(
                    "info"
                    if dashboard.warning_metric_count == 0
                    else "warning"
                ),
            ),
            RepositoryIntelligenceReportSection(
                name="Repository Summary",
                content="\n".join(summary_lines),
                status="info",
            ),
            RepositoryIntelligenceReportSection(
                name="Architecture Findings",
                content="\n".join(architecture_lines),
                status=(
                    "critical"
                    if architecture.critical_count > 0
                    else (
                        "warning"
                        if architecture.warning_count > 0
                        else "info"
                    )
                ),
            ),
            RepositoryIntelligenceReportSection(
                name="Warnings",
                content="\n".join(warning_lines),
                status=(
                    "warning"
                    if dashboard.warnings
                    else "info"
                ),
            ),
        ]

        return RepositoryIntelligenceReport(
            repository_path=str(root),
            repository_name=root.name,
            title=f"{root.name} Repository Intelligence Report",
            sections=sections,
        )
