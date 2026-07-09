from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OperatorSessionGuardRule:
    name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class OperatorSessionGuardReport:
    current_test_count: int
    target_test_count: int
    rules: list[OperatorSessionGuardRule] = field(default_factory=list)

    @property
    def delta(self) -> int:
        return self.target_test_count - self.current_test_count

    @property
    def is_forward_progress(self) -> bool:
        return self.delta > 0

    @property
    def rule_count(self) -> int:
        return len(self.rules)

    @property
    def passed_count(self) -> int:
        return sum(1 for rule in self.rules if rule.passed)

    @property
    def failed_count(self) -> int:
        return self.rule_count - self.passed_count

    @property
    def failed_rules(self) -> list[OperatorSessionGuardRule]:
        return [rule for rule in self.rules if not rule.passed]

    @property
    def passed(self) -> bool:
        return self.rule_count > 0 and self.failed_count == 0


class OperatorSessionGuardBuilder:
    def build(
        self,
        current_test_count: int,
        target_test_count: int,
        uses_python_file_writers: bool = True,
        avoids_nested_heredocs: bool = True,
        includes_test_run: bool = True,
        separates_commit_commands: bool = True,
    ) -> OperatorSessionGuardReport:
        delta = target_test_count - current_test_count

        rules = [
            OperatorSessionGuardRule(
                name="forward_progress",
                passed=delta > 0,
                message="Target test count is greater than current test count."
                if delta > 0
                else "Target test count must be greater than current test count.",
            ),
            OperatorSessionGuardRule(
                name="python_file_writers",
                passed=uses_python_file_writers,
                message="Implementation uses Python file writers."
                if uses_python_file_writers
                else "Implementation must use Python file writers.",
            ),
            OperatorSessionGuardRule(
                name="no_nested_heredocs",
                passed=avoids_nested_heredocs,
                message="Implementation avoids nested heredocs."
                if avoids_nested_heredocs
                else "Implementation must avoid nested heredocs.",
            ),
            OperatorSessionGuardRule(
                name="test_run_included",
                passed=includes_test_run,
                message="Implementation block includes test run."
                if includes_test_run
                else "Implementation block must include test run.",
            ),
            OperatorSessionGuardRule(
                name="commit_commands_separate",
                passed=separates_commit_commands,
                message="Commit commands are separated from implementation block."
                if separates_commit_commands
                else "Commit commands must be separated until tests pass.",
            ),
        ]

        return OperatorSessionGuardReport(
            current_test_count=current_test_count,
            target_test_count=target_test_count,
            rules=rules,
        )
