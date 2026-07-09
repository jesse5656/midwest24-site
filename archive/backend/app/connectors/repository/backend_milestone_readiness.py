from __future__ import annotations

from dataclasses import dataclass, field

from app.connectors.repository.backend_milestone import BackendMilestoneScorecard


@dataclass(frozen=True)
class BackendMilestoneReadinessCheck:
    name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class BackendMilestoneReadinessReport:
    checks: list[BackendMilestoneReadinessCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def failed_checks(self) -> list[BackendMilestoneReadinessCheck]:
        return [check for check in self.checks if not check.passed]

    @property
    def passed_count(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for check in self.checks if not check.passed)


class BackendMilestoneReadinessEvaluator:
    def evaluate(self, scorecard: BackendMilestoneScorecard) -> BackendMilestoneReadinessReport:
        return BackendMilestoneReadinessReport(
            checks=[
                BackendMilestoneReadinessCheck(
                    name="has_tests",
                    passed=scorecard.test_count > 0,
                    message=f"{scorecard.test_count} tests are passing."
                    if scorecard.test_count > 0
                    else "No passing tests are recorded.",
                ),
                BackendMilestoneReadinessCheck(
                    name="all_capabilities_complete",
                    passed=scorecard.is_complete,
                    message="All milestone capabilities are complete."
                    if scorecard.is_complete
                    else "Some milestone capabilities are incomplete.",
                ),
                BackendMilestoneReadinessCheck(
                    name="capability_coverage",
                    passed=scorecard.capability_count >= 7,
                    message=f"{scorecard.capability_count} milestone capabilities are tracked."
                    if scorecard.capability_count >= 7
                    else "Milestone capability coverage is incomplete.",
                ),
            ]
        )
