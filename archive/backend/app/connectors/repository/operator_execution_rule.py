from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OperatorExecutionRule:
    name: str
    instruction: str
    rationale: str
    required: bool = True


@dataclass(frozen=True)
class OperatorExecutionPrompt:
    test_count: int
    target_test_count: int
    rule: OperatorExecutionRule

    @property
    def delta(self) -> int:
        return self.target_test_count - self.test_count

    @property
    def is_forward_progress(self) -> bool:
        return self.delta > 0

    def render(self) -> str:
        return (
            f"{self.test_count} passed. Go to {self.target_test_count}. "
            "Write the code as one copy/paste-safe bash block using Python file writers. "
            "Avoid nested heredocs. Include make test at the end. "
            "Put commit commands separately."
        )


@dataclass(frozen=True)
class OperatorExecutionRuleSet:
    rules: list[OperatorExecutionRule] = field(default_factory=list)

    @property
    def rule_count(self) -> int:
        return len(self.rules)

    @property
    def required_count(self) -> int:
        return sum(1 for rule in self.rules if rule.required)

    @property
    def optional_count(self) -> int:
        return sum(1 for rule in self.rules if not rule.required)

    @property
    def is_complete(self) -> bool:
        return self.rule_count > 0 and self.required_count > 0


class OperatorExecutionRuleBuilder:
    def build_rule(self) -> OperatorExecutionRule:
        return OperatorExecutionRule(
            name="copy_paste_safe_code_blocks",
            instruction=(
                "Generate implementation blocks as one copy/paste-safe bash block "
                "using Python file writers. Avoid nested heredocs. Include test run "
                "at the end. Put commit/update commands in a separate second block "
                "only after tests pass."
            ),
            rationale="This prevents shell heredoc hangs and keeps implementation execution deterministic.",
            required=True,
        )

    def build_prompt(self, test_count: int, target_test_count: int) -> OperatorExecutionPrompt:
        return OperatorExecutionPrompt(
            test_count=test_count,
            target_test_count=target_test_count,
            rule=self.build_rule(),
        )

    def build_ruleset(self) -> OperatorExecutionRuleSet:
        return OperatorExecutionRuleSet(rules=[self.build_rule()])
