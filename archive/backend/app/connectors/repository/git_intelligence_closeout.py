from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.git_intelligence_readiness import (
    GitIntelligenceReadinessEvaluator,
    GitIntelligenceReadinessReport,
)
from app.connectors.repository.git_intelligence_report import GitIntelligenceReport


@dataclass(frozen=True)
class GitIntelligenceCloseout:
    objective_name: str
    status: str
    can_close: bool
    readiness: GitIntelligenceReadinessReport
    next_action: str


class GitIntelligenceCloseoutBuilder:
    def build(
        self,
        report: GitIntelligenceReport,
        objective_name: str = "Git Repository Intelligence",
    ) -> GitIntelligenceCloseout:
        readiness = GitIntelligenceReadinessEvaluator().evaluate(report)
        can_close = readiness.passed and report.is_ready

        return GitIntelligenceCloseout(
            objective_name=objective_name,
            status="ready_to_close" if can_close else "not_ready",
            can_close=can_close,
            readiness=readiness,
            next_action="Promote the next Priority Queue item."
            if can_close
            else "Resolve failed Git intelligence readiness checks before closing the objective.",
        )
