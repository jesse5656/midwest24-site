from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OperatorProgressTarget:
    current_test_count: int
    target_test_count: int

    @property
    def delta(self) -> int:
        return self.target_test_count - self.current_test_count

    @property
    def is_valid(self) -> bool:
        return self.delta > 0

    @property
    def percent_complete(self) -> float:
        if self.target_test_count <= 0:
            return 0.0
        return min(self.current_test_count / self.target_test_count, 1.0)

    @property
    def remaining_tests(self) -> int:
        return max(self.delta, 0)


@dataclass(frozen=True)
class OperatorProgressMilestone:
    name: str
    test_count: int
    reached: bool


@dataclass(frozen=True)
class OperatorProgressPlan:
    target: OperatorProgressTarget
    milestones: list[OperatorProgressMilestone] = field(default_factory=list)

    @property
    def milestone_count(self) -> int:
        return len(self.milestones)

    @property
    def reached_count(self) -> int:
        return sum(1 for milestone in self.milestones if milestone.reached)

    @property
    def unreached_count(self) -> int:
        return self.milestone_count - self.reached_count

    @property
    def next_milestone(self) -> OperatorProgressMilestone | None:
        for milestone in self.milestones:
            if not milestone.reached:
                return milestone
        return None


class OperatorProgressTargetBuilder:
    def build(self, current_test_count: int, target_test_count: int) -> OperatorProgressPlan:
        target = OperatorProgressTarget(
            current_test_count=current_test_count,
            target_test_count=target_test_count,
        )

        candidate_counts = [
            current_test_count,
            current_test_count + 20,
            current_test_count + 40,
            target_test_count,
        ]

        unique_counts = []
        for count in candidate_counts:
            bounded = min(count, target_test_count)
            if bounded not in unique_counts:
                unique_counts.append(bounded)

        milestones = [
            OperatorProgressMilestone(
                name=f"{count}_tests",
                test_count=count,
                reached=current_test_count >= count,
            )
            for count in unique_counts
        ]

        return OperatorProgressPlan(target=target, milestones=milestones)
