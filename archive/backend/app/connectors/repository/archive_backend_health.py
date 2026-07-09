from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.repository_health import (
    RepositoryHealthCheck,
    RepositoryHealthReport,
    RepositoryHealthReportBuilder,
)


@dataclass(frozen=True)
class ArchiveBackendHealthInputs:
    test_count: int
    has_progress_ledger: bool
    has_operating_plan: bool
    has_runbook: bool
    has_git_intelligence: bool
    has_code_intelligence: bool


class ArchiveBackendHealthEvaluator:
    def evaluate(self, inputs: ArchiveBackendHealthInputs) -> RepositoryHealthReport:
        checks = [
            RepositoryHealthCheck(
                name="tests_present",
                passed=inputs.test_count > 0,
                message=f"{inputs.test_count} tests are passing."
                if inputs.test_count > 0
                else "No passing test count was provided.",
                severity="error" if inputs.test_count <= 0 else "info",
            ),
            RepositoryHealthCheck(
                name="progress_ledger_present",
                passed=inputs.has_progress_ledger,
                message="Progress ledger is present."
                if inputs.has_progress_ledger
                else "Progress ledger is missing.",
                severity="error" if not inputs.has_progress_ledger else "info",
            ),
            RepositoryHealthCheck(
                name="operating_plan_present",
                passed=inputs.has_operating_plan,
                message="Operating Plan is present."
                if inputs.has_operating_plan
                else "Operating Plan is missing.",
                severity="error" if not inputs.has_operating_plan else "info",
            ),
            RepositoryHealthCheck(
                name="runbook_present",
                passed=inputs.has_runbook,
                message="Repository ingestion runbook is present."
                if inputs.has_runbook
                else "Repository ingestion runbook is missing.",
                severity="warning" if not inputs.has_runbook else "info",
            ),
            RepositoryHealthCheck(
                name="git_intelligence_present",
                passed=inputs.has_git_intelligence,
                message="Git Repository Intelligence is present."
                if inputs.has_git_intelligence
                else "Git Repository Intelligence is missing.",
                severity="warning" if not inputs.has_git_intelligence else "info",
            ),
            RepositoryHealthCheck(
                name="code_intelligence_present",
                passed=inputs.has_code_intelligence,
                message="Code Intelligence Preview is present."
                if inputs.has_code_intelligence
                else "Code Intelligence Preview is missing.",
                severity="warning" if not inputs.has_code_intelligence else "info",
            ),
        ]

        return RepositoryHealthReportBuilder().build("Archive Backend Health", checks)
