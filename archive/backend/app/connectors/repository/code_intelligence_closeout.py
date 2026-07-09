from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.code_intelligence_readiness import (
    CodeIntelligenceReadinessEvaluator,
    CodeIntelligenceReadinessReport,
)
from app.connectors.repository.code_intelligence_report import CodeIntelligenceReport


@dataclass(frozen=True)
class CodeIntelligenceCloseout:
    objective_name: str
    status: str
    can_close: bool
    readiness: CodeIntelligenceReadinessReport
    next_action: str


class CodeIntelligenceCloseoutBuilder:
    def build(
        self,
        report: CodeIntelligenceReport,
        objective_name: str = "Code Intelligence Preview",
    ) -> CodeIntelligenceCloseout:
        readiness = CodeIntelligenceReadinessEvaluator().evaluate(report)
        can_close = report.is_ready and readiness.passed

        return CodeIntelligenceCloseout(
            objective_name=objective_name,
            status="ready_to_close" if can_close else "not_ready",
            can_close=can_close,
            readiness=readiness,
            next_action="Promote the next Priority Queue item."
            if can_close
            else "Resolve failed code intelligence readiness checks before closing the objective.",
        )
