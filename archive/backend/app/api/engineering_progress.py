from fastapi import APIRouter, status

from app.connectors.repository.engineering_progress import (
    EngineeringCapability,
    EngineeringProgress,
    EngineeringProgressBuilder,
)
from app.connectors.repository.engineering_progress_summary import EngineeringProgressSummaryBuilder
from app.schemas.engineering_progress import (
    EngineeringCapabilityResponse,
    EngineeringProgressRequest,
    EngineeringProgressResponse,
    EngineeringProgressSummaryResponse,
)

router = APIRouter()


def serialize_engineering_capability(capability: EngineeringCapability) -> EngineeringCapabilityResponse:
    return EngineeringCapabilityResponse(
        name=capability.name,
        status=capability.status,
        evidence=capability.evidence,
        is_complete=capability.is_complete,
        is_in_progress=capability.is_in_progress,
        is_remaining=capability.is_remaining,
    )


def serialize_engineering_progress(progress: EngineeringProgress) -> EngineeringProgressResponse:
    summary = EngineeringProgressSummaryBuilder().build(progress)

    return EngineeringProgressResponse(
        milestone_name=progress.milestone_name,
        test_count=progress.test_count,
        capability_count=progress.capability_count,
        complete_count=progress.complete_count,
        in_progress_count=progress.in_progress_count,
        remaining_count=progress.remaining_count,
        percent_complete=progress.percent_complete,
        capabilities=[
            serialize_engineering_capability(capability)
            for capability in progress.capabilities
        ],
        completed_capabilities=[
            serialize_engineering_capability(capability)
            for capability in progress.completed_capabilities
        ],
        in_progress_capabilities=[
            serialize_engineering_capability(capability)
            for capability in progress.in_progress_capabilities
        ],
        remaining_capabilities=[
            serialize_engineering_capability(capability)
            for capability in progress.remaining_capabilities
        ],
        summary=EngineeringProgressSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/engineering-progress",
    response_model=EngineeringProgressResponse,
    status_code=status.HTTP_200_OK,
)
def get_engineering_progress(data: EngineeringProgressRequest):
    progress = EngineeringProgressBuilder().build(test_count=data.test_count)
    return serialize_engineering_progress(progress)
