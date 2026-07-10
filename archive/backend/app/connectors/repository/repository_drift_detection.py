from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_knowledge_graph import (
    RepositoryKnowledgeGraph,
    RepositoryKnowledgeGraphBuilder,
)


@dataclass(frozen=True)
class RepositoryDriftFinding:
    finding_type: str
    severity: str
    subject: str
    message: str


@dataclass(frozen=True)
class RepositoryDriftReport:
    baseline_repository_path: str
    candidate_repository_path: str
    findings: list[RepositoryDriftFinding] = field(default_factory=list)

    @property
    def finding_count(self) -> int:
        return len(self.findings)

    @property
    def has_drift(self) -> bool:
        return self.finding_count > 0

    @property
    def added_count(self) -> int:
        return sum(
            finding.finding_type.startswith("added_")
            for finding in self.findings
        )

    @property
    def removed_count(self) -> int:
        return sum(
            finding.finding_type.startswith("removed_")
            for finding in self.findings
        )

    @property
    def warning_count(self) -> int:
        return sum(
            finding.severity == "warning"
            for finding in self.findings
        )

    @property
    def critical_count(self) -> int:
        return sum(
            finding.severity == "critical"
            for finding in self.findings
        )

    @property
    def finding_types(self) -> list[str]:
        return sorted(
            {
                finding.finding_type
                for finding in self.findings
            }
        )

    @property
    def severity_levels(self) -> list[str]:
        return sorted(
            {
                finding.severity
                for finding in self.findings
            }
        )

    def findings_by_type(
        self,
        finding_type: str,
    ) -> list[RepositoryDriftFinding]:
        return [
            finding
            for finding in self.findings
            if finding.finding_type == finding_type
        ]


class RepositoryDriftDetector:
    def compare(
        self,
        baseline_repository_path: str | Path,
        candidate_repository_path: str | Path,
        max_depth: int = 8,
    ) -> RepositoryDriftReport:
        baseline_root = self._validate_repository(
            baseline_repository_path,
            "Baseline",
        )
        candidate_root = self._validate_repository(
            candidate_repository_path,
            "Candidate",
        )

        baseline = RepositoryKnowledgeGraphBuilder().build(
            baseline_root,
            max_depth=max_depth,
        )
        candidate = RepositoryKnowledgeGraphBuilder().build(
            candidate_root,
            max_depth=max_depth,
        )

        findings = [
            *self._compare_nodes(baseline, candidate),
            *self._compare_edges(baseline, candidate),
        ]

        return RepositoryDriftReport(
            baseline_repository_path=str(baseline_root),
            candidate_repository_path=str(candidate_root),
            findings=sorted(
                findings,
                key=lambda finding: (
                    finding.finding_type,
                    finding.subject,
                    finding.message,
                ),
            ),
        )

    def _validate_repository(
        self,
        repository_path: str | Path,
        label: str,
    ) -> Path:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(
                f"{label} repository path does not exist: {root}"
            )

        if not root.is_dir():
            raise NotADirectoryError(
                f"{label} repository path is not a directory: {root}"
            )

        return root

    def _compare_nodes(
        self,
        baseline: RepositoryKnowledgeGraph,
        candidate: RepositoryKnowledgeGraph,
    ) -> list[RepositoryDriftFinding]:
        baseline_nodes = {
            node.node_id: node
            for node in baseline.nodes
        }
        candidate_nodes = {
            node.node_id: node
            for node in candidate.nodes
        }

        findings: list[RepositoryDriftFinding] = []

        for node_id in sorted(
            set(candidate_nodes) - set(baseline_nodes)
        ):
            node = candidate_nodes[node_id]

            findings.append(
                RepositoryDriftFinding(
                    finding_type=f"added_{node.node_type}",
                    severity="info",
                    subject=node_id,
                    message=(
                        f"Candidate added {node.node_type} "
                        f"node {node.label}."
                    ),
                )
            )

        for node_id in sorted(
            set(baseline_nodes) - set(candidate_nodes)
        ):
            node = baseline_nodes[node_id]

            severity = (
                "critical"
                if node.node_type in {"dependency", "symbol"}
                else "warning"
            )

            findings.append(
                RepositoryDriftFinding(
                    finding_type=f"removed_{node.node_type}",
                    severity=severity,
                    subject=node_id,
                    message=(
                        f"Candidate removed {node.node_type} "
                        f"node {node.label}."
                    ),
                )
            )

        return findings

    def _compare_edges(
        self,
        baseline: RepositoryKnowledgeGraph,
        candidate: RepositoryKnowledgeGraph,
    ) -> list[RepositoryDriftFinding]:
        baseline_edges = {
            (
                edge.source_id,
                edge.target_id,
                edge.relationship,
            )
            for edge in baseline.edges
        }
        candidate_edges = {
            (
                edge.source_id,
                edge.target_id,
                edge.relationship,
            )
            for edge in candidate.edges
        }

        findings: list[RepositoryDriftFinding] = []

        for source_id, target_id, relationship in sorted(
            candidate_edges - baseline_edges
        ):
            findings.append(
                RepositoryDriftFinding(
                    finding_type="added_relationship",
                    severity="info",
                    subject=(
                        f"{source_id}->{target_id}:{relationship}"
                    ),
                    message=(
                        f"Candidate added relationship {relationship} "
                        f"from {source_id} to {target_id}."
                    ),
                )
            )

        for source_id, target_id, relationship in sorted(
            baseline_edges - candidate_edges
        ):
            findings.append(
                RepositoryDriftFinding(
                    finding_type="removed_relationship",
                    severity="warning",
                    subject=(
                        f"{source_id}->{target_id}:{relationship}"
                    ),
                    message=(
                        f"Candidate removed relationship {relationship} "
                        f"from {source_id} to {target_id}."
                    ),
                )
            )

        return findings
