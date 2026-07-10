from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_drift_detection import (
    RepositoryDriftReport,
)


@dataclass(frozen=True)
class RepositoryDriftSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryDriftSummaryBuilder:
    def build(
        self,
        report: RepositoryDriftReport,
    ) -> RepositoryDriftSummary:
        if not report.has_drift:
            return RepositoryDriftSummary(
                outcome="no_drift",
                message=(
                    "No repository architecture drift was detected."
                ),
                action_required=False,
            )

        if report.critical_count > 0:
            return RepositoryDriftSummary(
                outcome="critical_drift",
                message=(
                    f"Detected {report.finding_count} drift finding(s), "
                    f"including {report.critical_count} critical finding(s)."
                ),
                action_required=True,
            )

        return RepositoryDriftSummary(
            outcome="drift_detected",
            message=(
                f"Detected {report.finding_count} drift finding(s): "
                f"{report.added_count} addition(s), "
                f"{report.removed_count} removal(s), and "
                f"{report.warning_count} warning(s)."
            ),
            action_required=report.warning_count > 0,
        )
