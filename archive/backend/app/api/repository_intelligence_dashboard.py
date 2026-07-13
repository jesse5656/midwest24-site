from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_intelligence_dashboard import (
    RepositoryIntelligenceDashboard,
    RepositoryIntelligenceDashboardBuilder,
    RepositoryIntelligenceMetric,
)
from app.connectors.repository.repository_intelligence_dashboard_summary import (
    RepositoryIntelligenceDashboardSummaryBuilder,
)
from app.schemas.repository_intelligence_dashboard import (
    RepositoryIntelligenceDashboardRequest,
    RepositoryIntelligenceDashboardResponse,
    RepositoryIntelligenceDashboardSummaryResponse,
    RepositoryIntelligenceMetricResponse,
)

router = APIRouter()


def serialize_repository_intelligence_metric(
    metric: RepositoryIntelligenceMetric,
) -> RepositoryIntelligenceMetricResponse:
    return RepositoryIntelligenceMetricResponse(
        name=metric.name,
        value=metric.value,
        status=metric.status,
        description=metric.description,
    )


def serialize_repository_intelligence_dashboard(
    dashboard: RepositoryIntelligenceDashboard,
) -> RepositoryIntelligenceDashboardResponse:
    summary = RepositoryIntelligenceDashboardSummaryBuilder().build(
        dashboard
    )

    return RepositoryIntelligenceDashboardResponse(
        repository_path=dashboard.repository_path,
        repository_name=dashboard.repository_name,
        metrics=[
            serialize_repository_intelligence_metric(metric)
            for metric in dashboard.metrics
        ],
        warnings=dashboard.warnings,
        metric_count=dashboard.metric_count,
        warning_count=dashboard.warning_count,
        healthy_metric_count=dashboard.healthy_metric_count,
        warning_metric_count=dashboard.warning_metric_count,
        critical_metric_count=dashboard.critical_metric_count,
        is_healthy=dashboard.is_healthy,
        metric_names=dashboard.metric_names,
        summary=RepositoryIntelligenceDashboardSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-intelligence-dashboard",
    response_model=RepositoryIntelligenceDashboardResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_intelligence_dashboard(
    data: RepositoryIntelligenceDashboardRequest,
):
    try:
        dashboard = RepositoryIntelligenceDashboardBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )

        return serialize_repository_intelligence_dashboard(
            dashboard
        )

    except (FileNotFoundError, NotADirectoryError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
