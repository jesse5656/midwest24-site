from __future__ import annotations

from dataclasses import dataclass, field

from app.connectors.repository.git_intelligence_report import GitIntelligenceReport


@dataclass(frozen=True)
class GitIntelligenceReadinessCheck:
    name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class GitIntelligenceReadinessReport:
    checks: list[GitIntelligenceReadinessCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def failed_checks(self) -> list[GitIntelligenceReadinessCheck]:
        return [check for check in self.checks if not check.passed]

    @property
    def passed_count(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for check in self.checks if not check.passed)


class GitIntelligenceReadinessEvaluator:
    def evaluate(self, report: GitIntelligenceReport) -> GitIntelligenceReadinessReport:
        checks = [
            GitIntelligenceReadinessCheck(
                name="is_git_repository",
                passed=report.is_repository,
                message="Path is a Git repository."
                if report.is_repository
                else "Path is not a Git repository.",
            ),
            GitIntelligenceReadinessCheck(
                name="has_commits",
                passed=report.commit_count > 0,
                message="Git commits are available."
                if report.commit_count > 0
                else "No Git commits are available.",
            ),
            GitIntelligenceReadinessCheck(
                name="has_authorship",
                passed=report.author_count > 0,
                message="Git authorship is available."
                if report.author_count > 0
                else "No Git authorship is available.",
            ),
            GitIntelligenceReadinessCheck(
                name="file_change_preview_available",
                passed=report.file_change_count >= 0,
                message="Git file-change preview is available.",
            ),
        ]

        return GitIntelligenceReadinessReport(checks=checks)
