from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.objective_summary import RepositoryObjectiveSummary
from app.connectors.repository.readiness import RepositoryObjectiveReadinessEvaluator, RepositoryReadinessReport


@dataclass(frozen=True)
class RepositoryObjectiveCloseout:
    objective_name: str
    status: str
    can_close: bool
    readiness: RepositoryReadinessReport
    next_action: str


class RepositoryObjectiveCloseoutBuilder:
    def build(self, summary: RepositoryObjectiveSummary) -> RepositoryObjectiveCloseout:
        readiness = RepositoryObjectiveReadinessEvaluator().evaluate(summary)
        can_close = summary.is_complete and readiness.passed

        return RepositoryObjectiveCloseout(
            objective_name=summary.objective_name,
            status="ready_to_close" if can_close else "not_ready",
            can_close=can_close,
            readiness=readiness,
            next_action="Promote the next Priority Queue item."
            if can_close
            else "Resolve failed readiness checks before closing the objective.",
        )
