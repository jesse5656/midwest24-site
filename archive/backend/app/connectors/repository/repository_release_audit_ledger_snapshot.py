from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.connectors.repository.repository_release_audit_ledger import (
    GENESIS_HASH,
)
from app.connectors.repository.repository_release_audit_ledger_verification import (
    RepositoryReleaseAuditLedgerDocumentVerification,
    RepositoryReleaseAuditLedgerDocumentVerifier,
)


RELEASE_AUDIT_LEDGER_SNAPSHOT_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerSnapshotEntry:
    sequence: int
    bundle_id: str
    repository_name: str
    accepted: bool
    entry_hash: str


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerSnapshot:
    schema_version: str
    snapshot_id: str
    ledger_id: str
    ledger_integrity_valid: bool
    ledger_chain_valid: bool
    ledger_accepted: bool
    entry_count: int
    accepted_entry_count: int
    rejected_entry_count: int
    latest_entry_hash: str
    repository_names: list[str] = field(default_factory=list)
    entries: list[
        RepositoryReleaseAuditLedgerSnapshotEntry
    ] = field(default_factory=list)
    issue_codes: list[str] = field(default_factory=list)

    @property
    def accepted(self) -> bool:
        return (
            self.ledger_integrity_valid
            and self.ledger_chain_valid
            and self.ledger_accepted
            and self.rejected_entry_count == 0
            and not self.issue_codes
        )

    @property
    def rejected(self) -> bool:
        return not self.accepted

    @property
    def status(self) -> str:
        if self.accepted:
            return "ledger_snapshot_accepted"

        if not self.ledger_integrity_valid:
            return "ledger_snapshot_invalid_integrity"

        if not self.ledger_chain_valid:
            return "ledger_snapshot_invalid_chain"

        return "ledger_snapshot_rejected"

    @property
    def repository_count(self) -> int:
        return len(self.repository_names)

    @property
    def issue_count(self) -> int:
        return len(self.issue_codes)

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "ledger_id": self.ledger_id,
            "ledger_integrity_valid": (
                self.ledger_integrity_valid
            ),
            "ledger_chain_valid": self.ledger_chain_valid,
            "ledger_accepted": self.ledger_accepted,
            "entry_count": self.entry_count,
            "accepted_entry_count": (
                self.accepted_entry_count
            ),
            "rejected_entry_count": (
                self.rejected_entry_count
            ),
            "latest_entry_hash": self.latest_entry_hash,
            "repository_names": sorted(
                self.repository_names
            ),
            "entries": [
                {
                    "sequence": entry.sequence,
                    "bundle_id": entry.bundle_id,
                    "repository_name": entry.repository_name,
                    "accepted": entry.accepted,
                    "entry_hash": entry.entry_hash,
                }
                for entry in sorted(
                    self.entries,
                    key=lambda item: item.sequence,
                )
            ],
            "issue_codes": sorted(self.issue_codes),
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        )

    def as_json(self) -> str:
        payload = self.canonical_payload()
        payload["snapshot_id"] = self.snapshot_id
        payload["accepted"] = self.accepted
        payload["status"] = self.status

        return json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ) + "\n"

    def as_markdown(self) -> str:
        lines = [
            "# Repository Release Audit Ledger Snapshot",
            "",
            f"- **Snapshot ID:** `{self.snapshot_id}`",
            f"- **Ledger ID:** `{self.ledger_id}`",
            f"- **Entries:** {self.entry_count}",
            f"- **Accepted entries:** "
            f"{self.accepted_entry_count}",
            f"- **Rejected entries:** "
            f"{self.rejected_entry_count}",
            f"- **Repositories:** {self.repository_count}",
            f"- **Latest entry hash:** "
            f"`{self.latest_entry_hash}`",
            f"- **Status:** {self.status}",
            "",
            "## Ledger Entries",
            "",
        ]

        if not self.entries:
            lines.append("- No entries.")

        for entry in self.entries:
            lines.append(
                f"- **{entry.sequence}. "
                f"{entry.repository_name}** — "
                f"`{entry.bundle_id[:12]}` — "
                f"{'accepted' if entry.accepted else 'rejected'}"
            )

        if self.issue_codes:
            lines.extend(
                [
                    "",
                    "## Verification Issues",
                    "",
                ]
            )

            for code in self.issue_codes:
                lines.append(f"- `{code}`")

        return "\n".join(lines).rstrip() + "\n"


class RepositoryReleaseAuditLedgerSnapshotBuilder:
    def build(
        self,
        ledger_json: str,
        require_all_accepted: bool = True,
    ) -> RepositoryReleaseAuditLedgerSnapshot:
        try:
            payload = json.loads(ledger_json)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid release audit ledger JSON: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "Release audit ledger JSON must contain an object."
            )

        verification = (
            RepositoryReleaseAuditLedgerDocumentVerifier()
            .verify_json(
                ledger_json=ledger_json,
                require_all_accepted=require_all_accepted,
            )
        )

        return self.from_payload_and_verification(
            payload=payload,
            verification=verification,
        )

    def from_payload_and_verification(
        self,
        payload: dict[str, Any],
        verification: (
            RepositoryReleaseAuditLedgerDocumentVerification
        ),
    ) -> RepositoryReleaseAuditLedgerSnapshot:
        raw_entries = payload.get("entries", [])

        if not isinstance(raw_entries, list):
            raise ValueError(
                "Release audit ledger entries must be a list."
            )

        entries: list[
            RepositoryReleaseAuditLedgerSnapshotEntry
        ] = []

        repository_names: set[str] = set()

        for raw_entry in raw_entries:
            if not isinstance(raw_entry, dict):
                continue

            repository_name = str(
                raw_entry.get("repository_name", "")
            )

            if repository_name:
                repository_names.add(repository_name)

            entries.append(
                RepositoryReleaseAuditLedgerSnapshotEntry(
                    sequence=int(
                        raw_entry.get("sequence", 0)
                    ),
                    bundle_id=str(
                        raw_entry.get("bundle_id", "")
                    ),
                    repository_name=repository_name,
                    accepted=bool(
                        raw_entry.get("accepted", False)
                    ),
                    entry_hash=str(
                        raw_entry.get("entry_hash", "")
                    ),
                )
            )

        latest_entry_hash = (
            entries[-1].entry_hash
            if entries
            else GENESIS_HASH
        )

        provisional = RepositoryReleaseAuditLedgerSnapshot(
            schema_version=(
                RELEASE_AUDIT_LEDGER_SNAPSHOT_SCHEMA_VERSION
            ),
            snapshot_id="",
            ledger_id=verification.ledger_id,
            ledger_integrity_valid=(
                verification.integrity_valid
            ),
            ledger_chain_valid=verification.chain_valid,
            ledger_accepted=verification.accepted,
            entry_count=verification.entry_count,
            accepted_entry_count=(
                verification.accepted_entry_count
            ),
            rejected_entry_count=(
                verification.rejected_entry_count
            ),
            latest_entry_hash=latest_entry_hash,
            repository_names=sorted(repository_names),
            entries=entries,
            issue_codes=verification.issue_codes,
        )

        snapshot_id = hashlib.sha256(
            provisional.canonical_json().encode("utf-8")
        ).hexdigest()

        return RepositoryReleaseAuditLedgerSnapshot(
            schema_version=provisional.schema_version,
            snapshot_id=snapshot_id,
            ledger_id=provisional.ledger_id,
            ledger_integrity_valid=(
                provisional.ledger_integrity_valid
            ),
            ledger_chain_valid=(
                provisional.ledger_chain_valid
            ),
            ledger_accepted=provisional.ledger_accepted,
            entry_count=provisional.entry_count,
            accepted_entry_count=(
                provisional.accepted_entry_count
            ),
            rejected_entry_count=(
                provisional.rejected_entry_count
            ),
            latest_entry_hash=(
                provisional.latest_entry_hash
            ),
            repository_names=provisional.repository_names,
            entries=provisional.entries,
            issue_codes=provisional.issue_codes,
        )


def verify_release_audit_ledger_snapshot(
    snapshot: RepositoryReleaseAuditLedgerSnapshot,
) -> bool:
    expected = hashlib.sha256(
        snapshot.canonical_json().encode("utf-8")
    ).hexdigest()

    return expected == snapshot.snapshot_id
