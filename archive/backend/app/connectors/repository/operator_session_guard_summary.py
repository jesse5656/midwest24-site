from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.operator_session_guard import OperatorSessionGuardReport


@dataclass(frozen=True)
class OperatorSessionGuardSummary:
    outcome: str
    message: str
    action_required: bool


class OperatorSessionGuardSummaryBuilder:
    def build(self, report: OperatorSessionGuardReport) -> OperatorSessionGuardSummary:
        if report.rule_count == 0:
            return OperatorSessionGuardSummary(
                outcome="no_rules",
                message="Operator session guard has no rules.",
                action_required=True,
            )

        if report.passed:
            return OperatorSessionGuardSummary(
                outcome="ready",
                message=(
                    f"Operator session guard passed {report.passed_count}/{report.rule_count} "
                    f"rules and targets {report.delta} additional test(s)."
                ),
                action_required=False,
            )

        return OperatorSessionGuardSummary(
            outcome="blocked",
            message=(
                f"Operator session guard failed {report.failed_count}/{report.rule_count} rule(s)."
            ),
            action_required=True,
        )
