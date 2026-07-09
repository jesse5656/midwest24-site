from fastapi import APIRouter, status

from app.connectors.repository import (
    GitObjectiveScorecard,
    GitObjectiveScorecardBuilder,
    GitObjectiveSummaryBuilder,
)
from app.schemas.git_objective_scorecard import (
    GitObjectiveCapabilityResponse,
    GitObjectiveOperatorSummaryResponse,
    GitObjectiveScorecardRequest,
    GitObjectiveScorecardResponse,
)

router = APIRouter()


def serialize_git_objective_scorecard(scorecard: GitObjectiveScorecard) -> GitObjectiveScorecardResponse:
    summary = GitObjectiveSummaryBuilder().build(scorecard)

    return GitObjectiveScorecardResponse(
        objective_name=scorecard.objective_name,
        capabilities=[
            GitObjectiveCapabilityResponse(
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
        summary=GitObjectiveOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-git-objective-scorecard",
    response_model=GitObjectiveScorecardResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_git_objective_scorecard(data: GitObjectiveScorecardRequest):
    scorecard = GitObjectiveScorecardBuilder().build(test_count=data.test_count)
    return serialize_git_objective_scorecard(scorecard)
