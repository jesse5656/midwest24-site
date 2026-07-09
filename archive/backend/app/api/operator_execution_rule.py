from fastapi import APIRouter, status

from app.connectors.repository.operator_execution_rule import (
    OperatorExecutionPrompt,
    OperatorExecutionRule,
    OperatorExecutionRuleBuilder,
    OperatorExecutionRuleSet,
)
from app.connectors.repository.operator_execution_summary import OperatorExecutionSummaryBuilder
from app.schemas.operator_execution_rule import (
    OperatorExecutionEnvelopeResponse,
    OperatorExecutionPromptResponse,
    OperatorExecutionRuleRequest,
    OperatorExecutionRuleResponse,
    OperatorExecutionRuleSetResponse,
    OperatorExecutionSummaryResponse,
)

router = APIRouter()


def serialize_operator_execution_rule(rule: OperatorExecutionRule) -> OperatorExecutionRuleResponse:
    return OperatorExecutionRuleResponse(
        name=rule.name,
        instruction=rule.instruction,
        rationale=rule.rationale,
        required=rule.required,
    )


def serialize_operator_execution_ruleset(ruleset: OperatorExecutionRuleSet) -> OperatorExecutionRuleSetResponse:
    return OperatorExecutionRuleSetResponse(
        rules=[serialize_operator_execution_rule(rule) for rule in ruleset.rules],
        rule_count=ruleset.rule_count,
        required_count=ruleset.required_count,
        optional_count=ruleset.optional_count,
        is_complete=ruleset.is_complete,
    )


def serialize_operator_execution_prompt(prompt: OperatorExecutionPrompt) -> OperatorExecutionPromptResponse:
    return OperatorExecutionPromptResponse(
        test_count=prompt.test_count,
        target_test_count=prompt.target_test_count,
        delta=prompt.delta,
        is_forward_progress=prompt.is_forward_progress,
        rendered_prompt=prompt.render(),
        rule=serialize_operator_execution_rule(prompt.rule),
    )


def serialize_operator_execution_summary(summary) -> OperatorExecutionSummaryResponse:
    return OperatorExecutionSummaryResponse(
        outcome=summary.outcome,
        message=summary.message,
        action_required=summary.action_required,
    )


@router.post(
    "/api/v1/operator-execution-rule",
    response_model=OperatorExecutionEnvelopeResponse,
    status_code=status.HTTP_200_OK,
)
def get_operator_execution_rule(data: OperatorExecutionRuleRequest):
    builder = OperatorExecutionRuleBuilder()
    ruleset = builder.build_ruleset()
    prompt = builder.build_prompt(
        test_count=data.test_count,
        target_test_count=data.target_test_count,
    )
    summary_builder = OperatorExecutionSummaryBuilder()

    return OperatorExecutionEnvelopeResponse(
        ruleset=serialize_operator_execution_ruleset(ruleset),
        prompt=serialize_operator_execution_prompt(prompt),
        ruleset_summary=serialize_operator_execution_summary(
            summary_builder.build_for_ruleset(ruleset)
        ),
        prompt_summary=serialize_operator_execution_summary(
            summary_builder.build_for_prompt(prompt)
        ),
    )
