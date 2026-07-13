from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from app.connectors.repository.repository_release_audit_ledger_snapshot_verification import (
    RepositoryReleaseAuditLedgerSnapshotVerification,
    RepositoryReleaseAuditLedgerSnapshotVerifier,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerSnapshotComparisonEntry:
    sequence: int
    bundle_id: str
    repository_name: str
    accepted: bool
    entry_hash: str


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerSnapshotComparison:
    baseline_snapshot_id: str
    candidate_snapshot_id: str
    baseline_ledger_id: str
    candidate_ledger_id: str
    baseline_verification: (
        RepositoryReleaseAuditLedgerSnapshotVerification
    )
    candidate_verification: (
        RepositoryReleaseAuditLedgerSnapshotVerification
    )
    baseline_entries: list[
        RepositoryReleaseAuditLedgerSnapshotComparisonEntry
    ] = field(default_factory=list)
    candidate_entries: list[
        RepositoryReleaseAuditLedgerSnapshotComparisonEntry
    ] = field(default_factory=list)

    @property
    def baseline_entry_count(self) -> int:
        return len(self.baseline_entries)

    @property
    def candidate_entry_count(self) -> int:
        return len(self.candidate_entries)

    @property
    def entry_count_delta(self) -> int:
        return (
            self.candidate_entry_count
            - self.baseline_entry_count
        )

    @property
    def baseline_bundle_ids(self) -> list[str]:
        return [
            entry.bundle_id
            for entry in self.baseline_entries
        ]

    @property
    def candidate_bundle_ids(self) -> list[str]:
        return [
            entry.bundle_id
            for entry in self.candidate_entries
        ]

    @property
    def added_bundle_ids(self) -> list[str]:
        baseline_counts: dict[str, int] = {}

        for bundle_id in self.baseline_bundle_ids:
            baseline_counts[bundle_id] = (
                baseline_counts.get(bundle_id, 0) + 1
            )

        added: list[str] = []

        for bundle_id in self.candidate_bundle_ids:
            count = baseline_counts.get(bundle_id, 0)

            if count > 0:
                baseline_counts[bundle_id] = count - 1
            else:
                added.append(bundle_id)

        return added

    @property
    def removed_bundle_ids(self) -> list[str]:
        candidate_counts: dict[str, int] = {}

        for bundle_id in self.candidate_bundle_ids:
            candidate_counts[bundle_id] = (
                candidate_counts.get(bundle_id, 0) + 1
            )

        removed: list[str] = []

        for bundle_id in self.baseline_bundle_ids:
            count = candidate_counts.get(bundle_id, 0)

            if count > 0:
                candidate_counts[bundle_id] = count - 1
            else:
                removed.append(bundle_id)

        return removed

    @property
    def append_only(self) -> bool:
        if self.candidate_entry_count < self.baseline_entry_count:
            return False

        baseline_prefix = [
            (
                entry.sequence,
                entry.bundle_id,
                entry.repository_name,
                entry.accepted,
                entry.entry_hash,
            )
            for entry in self.baseline_entries
        ]

        candidate_prefix = [
            (
                entry.sequence,
                entry.bundle_id,
                entry.repository_name,
                entry.accepted,
                entry.entry_hash,
            )
            for entry in self.candidate_entries[
                : self.baseline_entry_count
            ]
        ]

        return baseline_prefix == candidate_prefix

    @property
    def history_rewritten(self) -> bool:
        return not self.append_only

    @property
    def acceptance_regression(self) -> bool:
        return (
            self.baseline_verification.accepted
            and not self.candidate_verification.accepted
        )

    @property
    def acceptance_improvement(self) -> bool:
        return (
            not self.baseline_verification.accepted
            and self.candidate_verification.accepted
        )

    @property
    def ledger_changed(self) -> bool:
        return self.baseline_ledger_id != self.candidate_ledger_id

    @property
    def snapshots_identical(self) -> bool:
        return (
            self.baseline_snapshot_id
            == self.candidate_snapshot_id
        )

    @property
    def changed(self) -> bool:
        return not self.snapshots_identical

    @property
    def safe_progression(self) -> bool:
        return (
            self.baseline_verification.valid
            and self.candidate_verification.valid
            and self.append_only
            and not self.acceptance_regression
            and not self.removed_bundle_ids
        )

    @property
    def status(self) -> str:
        if self.snapshots_identical:
            return "unchanged"

        if self.history_rewritten:
            return "history_rewritten"

        if self.acceptance_regression:
            return "acceptance_regression"

        if self.safe_progression:
            return "safe_progression"

        return "changed"


class RepositoryReleaseAuditLedgerSnapshotComparisonBuilder:
    def build(
        self,
        baseline_snapshot_json: str,
        candidate_snapshot_json: str,
        require_accepted: bool = False,
    ) -> RepositoryReleaseAuditLedgerSnapshotComparison:
        baseline_payload = self._load_snapshot(
            baseline_snapshot_json
        )
        candidate_payload = self._load_snapshot(
            candidate_snapshot_json
        )

        baseline_verification = (
            RepositoryReleaseAuditLedgerSnapshotVerifier()
            .verify_json(
                snapshot_json=baseline_snapshot_json,
                require_accepted=require_accepted,
            )
        )

        candidate_verification = (
            RepositoryReleaseAuditLedgerSnapshotVerifier()
            .verify_json(
                snapshot_json=candidate_snapshot_json,
                require_accepted=require_accepted,
            )
        )

        return RepositoryReleaseAuditLedgerSnapshotComparison(
            baseline_snapshot_id=str(
                baseline_payload["snapshot_id"]
            ),
            candidate_snapshot_id=str(
                candidate_payload["snapshot_id"]
            ),
            baseline_ledger_id=str(
                baseline_payload["ledger_id"]
            ),
            candidate_ledger_id=str(
                candidate_payload["ledger_id"]
            ),
            baseline_verification=baseline_verification,
            candidate_verification=candidate_verification,
            baseline_entries=self._entries(
                baseline_payload
            ),
            candidate_entries=self._entries(
                candidate_payload
            ),
        )

    def _load_snapshot(
        self,
        snapshot_json: str,
    ) -> dict[str, Any]:
        try:
            payload = json.loads(snapshot_json)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid ledger snapshot JSON: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "Ledger snapshot JSON must contain an object."
            )

        if "snapshot_id" not in payload:
            raise ValueError(
                "Ledger snapshot is missing snapshot_id."
            )

        if "ledger_id" not in payload:
            raise ValueError(
                "Ledger snapshot is missing ledger_id."
            )

        if not isinstance(payload.get("entries"), list):
            raise ValueError(
                "Ledger snapshot entries must be a list."
            )

        return payload

    def _entries(
        self,
        payload: dict[str, Any],
    ) -> list[
        RepositoryReleaseAuditLedgerSnapshotComparisonEntry
    ]:
        entries = []

        for raw_entry in payload["entries"]:
            if not isinstance(raw_entry, dict):
                continue

            entries.append(
                RepositoryReleaseAuditLedgerSnapshotComparisonEntry(
                    sequence=int(
                        raw_entry.get("sequence", 0)
                    ),
                    bundle_id=str(
                        raw_entry.get("bundle_id", "")
                    ),
                    repository_name=str(
                        raw_entry.get("repository_name", "")
                    ),
                    accepted=bool(
                        raw_entry.get("accepted", False)
                    ),
                    entry_hash=str(
                        raw_entry.get("entry_hash", "")
                    ),
                )
            )

        return sorted(
            entries,
            key=lambda entry: entry.sequence,
        )
