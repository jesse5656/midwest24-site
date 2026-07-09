from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_health import RepositoryHealthReport


@dataclass(frozen=True)
class RepositoryHealthOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryHealthSummaryBuilder:
    def build(self, report: RepositoryHealthReport) -> RepositoryHealthOperatorSummary:
        if report.check_count == 0:
            return RepositoryHealthOperatorSummary(
                outcome="no_checks",
                message=f"{report.name} has no health checks.",
                action_required=True,
            )

        if report.passed:
            return RepositoryHealthOperatorSummary(
                outcome="healthy",
                message=f"{report.name} passed {report.passed_count}/{report.check_count} health checks.",
                action_required=False,
            )

        if report.error_count > 0:
            return RepositoryHealthOperatorSummary(
                outcome="unhealthy",
                message=(
                    f"{report.name} failed {report.failed_count}/{report.check_count} health checks "
                    f"with {report.error_count} error(s)."
                ),
                action_required=True,
            )

        return RepositoryHealthOperatorSummary(
            outcome="warnings",
            message=(
                f"{report.name} has {report.failed_count} warning check(s) requiring review."
            ),
            action_required=False,
        )
