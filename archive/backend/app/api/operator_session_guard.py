from fastapi import APIRouter, status

from app.connectors.repository.operator_session_guard import (
    OperatorSessionGuardBuilder,
    OperatorSessionGuardReport,
    OperatorSessionGuardRule,
)
from app.connectors.repository.operator_session_guard_summary import OperatorSessionGuardSummaryBuilder
from app.schemas.operator_session_guard import (
    OperatorSessionGuardReportResponse,
    OperatorSessionGuardRequest,
    OperatorSessionGuardRuleResponse,
    OperatorSessionGuardSummaryResponse,
)

router = APIRouter()


def serialize_operator_session_guard_rule(rule: OperatorSessionGuardRule) -> OperatorSessionGuardRuleResponse:
    return OperatorSessionGuardRuleResponse(
        name=rule.name,
        passed=rule.passed,
        message=rule.message,
    )


def serialize_operator_session_guard_report(
    report: OperatorSessionGuardReport,
) -> OperatorSessionGuardReportResponse:
    summary = OperatorSessionGuardSummaryBuilder().build(report)

    return OperatorSessionGuardReportResponse(
        current_test_count=report.current_test_count,
        target_test_count=report.target_test_count,
        delta=report.delta,
        is_forward_progress=report.is_forward_progress,
        rule_count=report.rule_count,
        passed_count=report.passed_count,
        failed_count=report.failed_count,
        passed=report.passed,
        rules=[serialize_operator_session_guard_rule(rule) for rule in report.rules],
        failed_rules=[serialize_operator_session_guard_rule(rule) for rule in report.failed_rules],
        summary=OperatorSessionGuardSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/operator-session-guard",
    response_model=OperatorSessionGuardReportResponse,
    status_code=status.HTTP_200_OK,
)
def get_operator_session_guard(data: OperatorSessionGuardRequest):
    report = OperatorSessionGuardBuilder().build(
        current_test_count=data.current_test_count,
        target_test_count=data.target_test_count,
        uses_python_file_writers=data.uses_python_file_writers,
        avoids_nested_heredocs=data.avoids_nested_heredocs,
        includes_test_run=data.includes_test_run,
        separates_commit_commands=data.separates_commit_commands,
    )
    return serialize_operator_session_guard_report(report)
