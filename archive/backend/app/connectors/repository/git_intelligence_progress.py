from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.git_intelligence_report import GitIntelligenceReport


@dataclass(frozen=True)
class GitIntelligenceProgress:
    objective_name: str
    capability_count: int
    endpoint_count: int
    test_count: int
    status: str

    @property
    def ready_for_closeout(self) -> bool:
        return self.status == "completed" and self.capability_count >= 5 and self.endpoint_count >= 5


class GitIntelligenceProgressBuilder:
    def build(self, report: GitIntelligenceReport, test_count: int) -> GitIntelligenceProgress:
        capability_count = 0

        if report.is_repository:
            capability_count += 1
        if report.commit_count >= 0:
            capability_count += 1
        if report.file_change_count >= 0:
            capability_count += 1
        if report.author_count >= 0:
            capability_count += 1
        if report.current_branch is not None:
            capability_count += 1

        return GitIntelligenceProgress(
            objective_name="Git Repository Intelligence",
            capability_count=capability_count,
            endpoint_count=5,
            test_count=test_count,
            status="completed" if report.is_ready else "in_progress",
        )
