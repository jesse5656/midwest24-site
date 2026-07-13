from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_release_readiness import (
    RepositoryReleaseReadiness,
)


@dataclass(frozen=True)
class RepositoryReleaseReadinessSummary:
    outcome: str
    message: str
    action_required: bool


class RepositoryReleaseReadinessSummaryBuilder:
    def build(
        self,
        readiness: RepositoryReleaseReadiness,
    ) -> RepositoryReleaseReadinessSummary:
        if readiness.release_ready:
            return RepositoryReleaseReadinessSummary(
                outcome="release_ready",
                message=(
                    f"{readiness.repository_name} passed all "
                    f"{readiness.check_count} release-readiness checks."
                ),
                action_required=False,
            )

        if readiness.critical_failure_count > 0:
            return RepositoryReleaseReadinessSummary(
                outcome="release_blocked_critical",
                message=(
                    f"{readiness.repository_name} failed "
                    f"{readiness.failed_check_count} readiness check(s), "
                    f"including {readiness.critical_failure_count} "
                    f"critical failure(s)."
                ),
                action_required=True,
            )

        return RepositoryReleaseReadinessSummary(
            outcome="release_blocked",
            message=(
                f"{readiness.repository_name} failed "
                f"{readiness.failed_check_count} release-readiness "
                f"check(s)."
            ),
            action_required=True,
        )
