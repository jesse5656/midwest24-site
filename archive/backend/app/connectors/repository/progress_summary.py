from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.progress_ledger import RepositoryProgressLedger


@dataclass(frozen=True)
class RepositoryProgressSummary:
    repository: str
    latest_test_count: int
    checkpoint_count: int
    completed_count: int
    status: str
    message: str


class RepositoryProgressSummaryBuilder:
    def build(self, ledger: RepositoryProgressLedger) -> RepositoryProgressSummary:
        latest = ledger.latest

        if latest is None:
            return RepositoryProgressSummary(
                repository=ledger.repository,
                latest_test_count=0,
                checkpoint_count=0,
                completed_count=0,
                status="empty",
                message="No progress checkpoints have been recorded.",
            )

        return RepositoryProgressSummary(
            repository=ledger.repository,
            latest_test_count=ledger.latest_test_count,
            checkpoint_count=ledger.checkpoint_count,
            completed_count=ledger.completed_count,
            status=latest.status,
            message=f"Latest checkpoint '{latest.name}' recorded {latest.test_count} passing tests.",
        )
