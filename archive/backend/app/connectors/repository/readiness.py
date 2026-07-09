from __future__ import annotations

from dataclasses import dataclass, field

from app.connectors.repository.objective_summary import RepositoryObjectiveSummary


@dataclass(frozen=True)
class RepositoryReadinessCheck:
    name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class RepositoryReadinessReport:
    checks: list[RepositoryReadinessCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def failed_checks(self) -> list[RepositoryReadinessCheck]:
        return [check for check in self.checks if not check.passed]

    @property
    def passed_count(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for check in self.checks if not check.passed)


class RepositoryObjectiveReadinessEvaluator:
    def evaluate(self, summary: RepositoryObjectiveSummary) -> RepositoryReadinessReport:
        checks = [
            RepositoryReadinessCheck(
                name="no_failures",
                passed=summary.total_failures == 0,
                message="Repository ingestion has no recorded failures."
                if summary.total_failures == 0
                else f"Repository ingestion has {summary.total_failures} recorded failure(s).",
            ),
            RepositoryReadinessCheck(
                name="documents_created",
                passed=summary.total_documents > 0,
                message="Repository ingestion created documents."
                if summary.total_documents > 0
                else "Repository ingestion has not created any documents.",
            ),
            RepositoryReadinessCheck(
                name="jobs_created",
                passed=summary.total_processing_jobs > 0,
                message="Repository ingestion created processing jobs."
                if summary.total_processing_jobs > 0
                else "Repository ingestion has not created any processing jobs.",
            ),
            RepositoryReadinessCheck(
                name="no_action_required",
                passed=not summary.action_required,
                message="No operator action is required."
                if not summary.action_required
                else "Operator action is required before closing this objective.",
            ),
        ]

        return RepositoryReadinessReport(checks=checks)
