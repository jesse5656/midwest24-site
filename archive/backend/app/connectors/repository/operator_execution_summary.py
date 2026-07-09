from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.operator_execution_rule import (
    OperatorExecutionPrompt,
    OperatorExecutionRuleSet,
)


@dataclass(frozen=True)
class OperatorExecutionSummary:
    outcome: str
    message: str
    action_required: bool


class OperatorExecutionSummaryBuilder:
    def build_for_ruleset(self, ruleset: OperatorExecutionRuleSet) -> OperatorExecutionSummary:
        if not ruleset.rules:
            return OperatorExecutionSummary(
                outcome="no_rules",
                message="No operator execution rules are defined.",
                action_required=True,
            )

        if ruleset.required_count == 0:
            return OperatorExecutionSummary(
                outcome="no_required_rules",
                message="Operator execution rules exist, but none are required.",
                action_required=True,
            )

        return OperatorExecutionSummary(
            outcome="ready",
            message=f"{ruleset.required_count} required operator execution rule(s) are active.",
            action_required=False,
        )

    def build_for_prompt(self, prompt: OperatorExecutionPrompt) -> OperatorExecutionSummary:
        if not prompt.is_forward_progress:
            return OperatorExecutionSummary(
                outcome="invalid_target",
                message="Target test count must be greater than current test count.",
                action_required=True,
            )

        return OperatorExecutionSummary(
            outcome="ready",
            message=f"Prompt targets {prompt.delta} additional passing test(s).",
            action_required=False,
        )
