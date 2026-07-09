from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RepositoryHealthCheck:
    name: str
    passed: bool
    message: str
    severity: str = "info"


@dataclass(frozen=True)
class RepositoryHealthReport:
    name: str
    checks: list[RepositoryHealthCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def check_count(self) -> int:
        return len(self.checks)

    @property
    def passed_count(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for check in self.checks if not check.passed)

    @property
    def failed_checks(self) -> list[RepositoryHealthCheck]:
        return [check for check in self.checks if not check.passed]

    @property
    def warning_count(self) -> int:
        return sum(1 for check in self.checks if check.severity == "warning")

    @property
    def error_count(self) -> int:
        return sum(1 for check in self.checks if check.severity == "error")


class RepositoryHealthReportBuilder:
    def build(self, name: str, checks: list[RepositoryHealthCheck]) -> RepositoryHealthReport:
        return RepositoryHealthReport(name=name, checks=checks)
