from fastapi import APIRouter, status

from app.connectors.repository import (
    CodeObjectiveScorecard,
    CodeObjectiveScorecardBuilder,
    CodeObjectiveSummaryBuilder,
)
from app.schemas.code_objective_scorecard import (
    CodeObjectiveCapabilityResponse,
    CodeObjectiveOperatorSummaryResponse,
    CodeObjectiveScorecardRequest,
    CodeObjectiveScorecardResponse,
)

router = APIRouter()


def serialize_code_objective_scorecard(scorecard: CodeObjectiveScorecard) -> CodeObjectiveScorecardResponse:
    summary = CodeObjectiveSummaryBuilder().build(scorecard)

    return CodeObjectiveScorecardResponse(
        objective_name=scorecard.objective_name,
        capabilities=[
            CodeObjectiveCapabilityResponse(
                name=capability.name,
                completed=capability.completed,
                evidence=capability.evidence,
            )
            for capability in scorecard.capabilities
        ],
        test_count=scorecard.test_count,
        capability_count=scorecard.capability_count,
        completed_capability_count=scorecard.completed_capability_count,
        incomplete_capability_count=scorecard.incomplete_capability_count,
        completion_ratio=scorecard.completion_ratio,
        is_complete=scorecard.is_complete,
        summary=CodeObjectiveOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-code-objective-scorecard",
    response_model=CodeObjectiveScorecardResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_code_objective_scorecard(data: CodeObjectiveScorecardRequest):
    scorecard = CodeObjectiveScorecardBuilder().build(test_count=data.test_count)
    return serialize_code_objective_scorecard(scorecard)
