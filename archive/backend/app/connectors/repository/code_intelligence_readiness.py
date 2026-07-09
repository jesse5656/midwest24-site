from __future__ import annotations

from dataclasses import dataclass, field

from app.connectors.repository.code_intelligence_report import CodeIntelligenceReport


@dataclass(frozen=True)
class CodeIntelligenceReadinessCheck:
    name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class CodeIntelligenceReadinessReport:
    checks: list[CodeIntelligenceReadinessCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def failed_checks(self) -> list[CodeIntelligenceReadinessCheck]:
        return [check for check in self.checks if not check.passed]

    @property
    def passed_count(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for check in self.checks if not check.passed)


class CodeIntelligenceReadinessEvaluator:
    def evaluate(self, report: CodeIntelligenceReport) -> CodeIntelligenceReadinessReport:
        return CodeIntelligenceReadinessReport(
            checks=[
                CodeIntelligenceReadinessCheck(
                    name="has_inventory",
                    passed=report.has_inventory,
                    message="Repository inventory is available."
                    if report.has_inventory
                    else "Repository inventory is empty.",
                ),
                CodeIntelligenceReadinessCheck(
                    name="has_languages",
                    passed=report.language_count > 0,
                    message="Repository languages are available."
                    if report.language_count > 0
                    else "No repository languages were detected.",
                ),
                CodeIntelligenceReadinessCheck(
                    name="has_symbols",
                    passed=report.has_outline,
                    message="Source symbols are available."
                    if report.has_outline
                    else "No source symbols were detected.",
                ),
            ]
        )
