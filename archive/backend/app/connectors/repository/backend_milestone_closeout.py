from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.backend_milestone import BackendMilestoneScorecard
from app.connectors.repository.backend_milestone_readiness import (
    BackendMilestoneReadinessEvaluator,
    BackendMilestoneReadinessReport,
)


@dataclass(frozen=True)
class BackendMilestoneCloseout:
    milestone_name: str
    status: str
    can_close: bool
    readiness: BackendMilestoneReadinessReport
    next_action: str


class BackendMilestoneCloseoutBuilder:
    def build(self, scorecard: BackendMilestoneScorecard) -> BackendMilestoneCloseout:
        readiness = BackendMilestoneReadinessEvaluator().evaluate(scorecard)
        can_close = scorecard.is_complete and readiness.passed

        return BackendMilestoneCloseout(
            milestone_name=scorecard.milestone_name,
            status="ready_to_close" if can_close else "not_ready",
            can_close=can_close,
            readiness=readiness,
            next_action="Prepare session transition prompt."
            if can_close
            else "Resolve failed backend milestone readiness checks.",
        )
