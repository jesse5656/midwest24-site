from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RepositoryProgressCheckpoint:
    name: str
    test_count: int
    status: str
    notes: str = ""


@dataclass(frozen=True)
class RepositoryProgressLedger:
    repository: str
    checkpoints: list[RepositoryProgressCheckpoint] = field(default_factory=list)

    @property
    def latest(self) -> RepositoryProgressCheckpoint | None:
        if not self.checkpoints:
            return None
        return self.checkpoints[-1]

    @property
    def latest_test_count(self) -> int:
        if self.latest is None:
            return 0
        return self.latest.test_count

    @property
    def checkpoint_count(self) -> int:
        return len(self.checkpoints)

    @property
    def completed_count(self) -> int:
        return sum(1 for checkpoint in self.checkpoints if checkpoint.status == "completed")

    def add_checkpoint(self, checkpoint: RepositoryProgressCheckpoint) -> "RepositoryProgressLedger":
        return RepositoryProgressLedger(
            repository=self.repository,
            checkpoints=[*self.checkpoints, checkpoint],
        )


class RepositoryProgressLedgerStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> RepositoryProgressLedger:
        if not self.path.exists():
            return RepositoryProgressLedger(repository="", checkpoints=[])

        raw = json.loads(self.path.read_text(encoding="utf-8"))

        return RepositoryProgressLedger(
            repository=raw.get("repository", ""),
            checkpoints=[
                RepositoryProgressCheckpoint(**checkpoint)
                for checkpoint in raw.get("checkpoints", [])
            ],
        )

    def save(self, ledger: RepositoryProgressLedger) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.path.write_text(
            json.dumps(asdict(ledger), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
