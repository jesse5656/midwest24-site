from fastapi import APIRouter, status

from app.connectors.repository.operator_progress_summary import OperatorProgressSummaryBuilder
from app.connectors.repository.operator_progress_target import (
    OperatorProgressMilestone,
    OperatorProgressPlan,
    OperatorProgressTarget,
    OperatorProgressTargetBuilder,
)
from app.schemas.operator_progress_target import (
    OperatorProgressMilestoneResponse,
    OperatorProgressPlanResponse,
    OperatorProgressSummaryResponse,
    OperatorProgressTargetRequest,
    OperatorProgressTargetResponse,
)

router = APIRouter()


def serialize_operator_progress_target(target: OperatorProgressTarget) -> OperatorProgressTargetResponse:
    return OperatorProgressTargetResponse(
        current_test_count=target.current_test_count,
        target_test_count=target.target_test_count,
        delta=target.delta,
        is_valid=target.is_valid,
        percent_complete=target.percent_complete,
        remaining_tests=target.remaining_tests,
    )


def serialize_operator_progress_milestone(
    milestone: OperatorProgressMilestone | None,
):
    if milestone is None:
        return None

    return OperatorProgressMilestoneResponse(
        name=milestone.name,
        test_count=milestone.test_count,
        reached=milestone.reached,
    )


def serialize_operator_progress_plan(plan: OperatorProgressPlan) -> OperatorProgressPlanResponse:
    summary = OperatorProgressSummaryBuilder().build(plan)

    return OperatorProgressPlanResponse(
        target=serialize_operator_progress_target(plan.target),
        milestones=[
            serialize_operator_progress_milestone(milestone)
            for milestone in plan.milestones
        ],
        milestone_count=plan.milestone_count,
        reached_count=plan.reached_count,
        unreached_count=plan.unreached_count,
        next_milestone=serialize_operator_progress_milestone(plan.next_milestone),
        summary=OperatorProgressSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/operator-progress-target",
    response_model=OperatorProgressPlanResponse,
    status_code=status.HTTP_200_OK,
)
def get_operator_progress_target(data: OperatorProgressTargetRequest):
    plan = OperatorProgressTargetBuilder().build(
        current_test_count=data.current_test_count,
        target_test_count=data.target_test_count,
    )
    return serialize_operator_progress_plan(plan)
