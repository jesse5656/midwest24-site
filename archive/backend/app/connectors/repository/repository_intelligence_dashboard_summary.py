from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_intelligence_dashboard import (
    RepositoryIntelligenceDashboard,
)


@dataclass(frozen=True)
class RepositoryIntelligenceDashboardSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryIntelligenceDashboardSummaryBuilder:
    def build(
        self,
        dashboard: RepositoryIntelligenceDashboard,
    ) -> RepositoryIntelligenceDashboardSummary:
        if dashboard.metric_count == 0:
            return RepositoryIntelligenceDashboardSummary(
                outcome="empty_dashboard",
                message=(
                    "Repository intelligence dashboard has no metrics."
                ),
                action_required=True,
            )

        if dashboard.critical_metric_count > 0:
            return RepositoryIntelligenceDashboardSummary(
                outcome="critical",
                message=(
                    f"{dashboard.repository_name} dashboard contains "
                    f"{dashboard.critical_metric_count} critical metric(s)."
                ),
                action_required=True,
            )

        if not dashboard.is_healthy:
            return RepositoryIntelligenceDashboardSummary(
                outcome="warnings_detected",
                message=(
                    f"{dashboard.repository_name} dashboard contains "
                    f"{dashboard.metric_count} metric(s), "
                    f"{dashboard.healthy_metric_count} healthy metric(s), "
                    f"and {dashboard.warning_count} warning(s)."
                ),
                action_required=True,
            )

        return RepositoryIntelligenceDashboardSummary(
            outcome="healthy",
            message=(
                f"{dashboard.repository_name} dashboard contains "
                f"{dashboard.metric_count} healthy metric(s) "
                f"with no warnings."
            ),
            action_required=False,
        )
