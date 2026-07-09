from fastapi import APIRouter, status

from app.connectors.repository.milestone_closeout_package import (
    MilestoneCloseoutPackage,
    MilestoneCloseoutPackageBuilder,
)
from app.connectors.repository.milestone_closeout_summary import MilestoneCloseoutSummaryBuilder
from app.schemas.milestone_closeout_package import (
    MilestoneCloseoutItemResponse,
    MilestoneCloseoutPackageRequest,
    MilestoneCloseoutPackageResponse,
    MilestoneCloseoutSummaryResponse,
)

router = APIRouter()


def serialize_milestone_closeout_package(
    package: MilestoneCloseoutPackage,
) -> MilestoneCloseoutPackageResponse:
    summary = MilestoneCloseoutSummaryBuilder().build(package)

    return MilestoneCloseoutPackageResponse(
        milestone_name=package.milestone_name,
        test_count=package.test_count,
        items=[
            MilestoneCloseoutItemResponse(
                name=item.name,
                completed=item.completed,
                evidence=item.evidence,
            )
            for item in package.items
        ],
        item_count=package.item_count,
        completed_count=package.completed_count,
        incomplete_count=package.incomplete_count,
        is_complete=package.is_complete,
        completion_ratio=package.completion_ratio,
        summary=MilestoneCloseoutSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/milestone-closeout-package",
    response_model=MilestoneCloseoutPackageResponse,
    status_code=status.HTTP_200_OK,
)
def get_milestone_closeout_package(data: MilestoneCloseoutPackageRequest):
    package = MilestoneCloseoutPackageBuilder().build(test_count=data.test_count)
    return serialize_milestone_closeout_package(package)
