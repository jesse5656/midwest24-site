from fastapi import APIRouter, status

from app.connectors.repository.operator_execution_checklist import (
    OperatorExecutionChecklist,
    OperatorExecutionChecklistBuilder,
)
from app.connectors.repository.operator_execution_checklist_summary import (
    OperatorExecutionChecklistSummaryBuilder,
)
from app.schemas.operator_execution_checklist import (
    OperatorExecutionChecklistItemResponse,
    OperatorExecutionChecklistResponse,
    OperatorExecutionChecklistSummaryResponse,
)

router = APIRouter()


def serialize_operator_execution_checklist(
    checklist: OperatorExecutionChecklist,
) -> OperatorExecutionChecklistResponse:
    summary = OperatorExecutionChecklistSummaryBuilder().build(checklist)

    return OperatorExecutionChecklistResponse(
        name=checklist.name,
        items=[
            OperatorExecutionChecklistItemResponse(
                name=item.name,
                completed=item.completed,
                evidence=item.evidence,
            )
            for item in checklist.items
        ],
        item_count=checklist.item_count,
        completed_count=checklist.completed_count,
        incomplete_count=checklist.incomplete_count,
        is_complete=checklist.is_complete,
        summary=OperatorExecutionChecklistSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.get(
    "/api/v1/operator-execution-checklist",
    response_model=OperatorExecutionChecklistResponse,
    status_code=status.HTTP_200_OK,
)
def get_operator_execution_checklist():
    checklist = OperatorExecutionChecklistBuilder().build()
    return serialize_operator_execution_checklist(checklist)
