from fastapi import APIRouter, status

from app.connectors.repository import (
    BackendMilestoneCloseoutBuilder,
    BackendMilestoneScorecard,
    BackendMilestoneScorecardBuilder,
    BackendMilestoneSummaryBuilder,
)
from app.schemas.backend_milestone import (
    BackendMilestoneCapabilityResponse,
    BackendMilestoneCloseoutResponse,
    BackendMilestoneOperatorSummaryResponse,
    BackendMilestoneReadinessCheckResponse,
    BackendMilestoneReadinessReportResponse,
    BackendMilestoneScorecardRequest,
    BackendMilestoneScorecardResponse,
)

router = APIRouter()


def serialize_backend_milestone_readiness(readiness) -> BackendMilestoneReadinessReportResponse:
    return BackendMilestoneReadinessReportResponse(
        checks=[
            BackendMilestoneReadinessCheckResponse(
                name=check.name,
                passed=check.passed,
                message=check.message,
            )
            for check in readiness.checks
        ],
        passed=readiness.passed,
        passed_count=readiness.passed_count,
        failed_count=readiness.failed_count,
    )


def serialize_backend_milestone_scorecard(
    scorecard: BackendMilestoneScorecard,
) -> BackendMilestoneScorecardResponse:
    summary = BackendMilestoneSummaryBuilder().build(scorecard)
    closeout = BackendMilestoneCloseoutBuilder().build(scorecard)

    return BackendMilestoneScorecardResponse(
        milestone_name=scorecard.milestone_name,
        test_count=scorecard.test_count,
        capabilities=[
            BackendMilestoneCapabilityResponse(
                name=capability.name,
                completed=capability.completed,
                evidence=capability.evidence,
            )
            for capability in scorecard.capabilities
        ],
        capability_count=scorecard.capability_count,
        completed_capability_count=scorecard.completed_capability_count,
        incomplete_capability_count=scorecard.incomplete_capability_count,
        completion_ratio=scorecard.completion_ratio,
        is_complete=scorecard.is_complete,
        summary=BackendMilestoneOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
        closeout=BackendMilestoneCloseoutResponse(
            milestone_name=closeout.milestone_name,
            status=closeout.status,
            can_close=closeout.can_close,
            readiness=serialize_backend_milestone_readiness(closeout.readiness),
            next_action=closeout.next_action,
        ),
    )


@router.post(
    "/api/v1/archive-backend-milestone-scorecard",
    response_model=BackendMilestoneScorecardResponse,
    status_code=status.HTTP_200_OK,
)
def get_archive_backend_milestone_scorecard(data: BackendMilestoneScorecardRequest):
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=data.test_count)
    return serialize_backend_milestone_scorecard(scorecard)
