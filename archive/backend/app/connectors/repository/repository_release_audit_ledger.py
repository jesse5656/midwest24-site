from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.connectors.repository.repository_release_audit_bundle_verification import (
    RepositoryReleaseAuditBundleVerification,
    RepositoryReleaseAuditBundleVerifier,
)


RELEASE_AUDIT_LEDGER_SCHEMA_VERSION = "1.0"
GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerEntry:
    sequence: int
    bundle_id: str
    repository_name: str
    accepted: bool
    previous_entry_hash: str
    entry_hash: str

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "bundle_id": self.bundle_id,
            "repository_name": self.repository_name,
            "accepted": self.accepted,
            "previous_entry_hash": self.previous_entry_hash,
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        )


@dataclass(frozen=True)
class RepositoryReleaseAuditLedger:
    schema_version: str
    ledger_id: str
    entries: list[RepositoryReleaseAuditLedgerEntry] = field(
        default_factory=list
    )

    @property
    def entry_count(self) -> int:
        return len(self.entries)

    @property
    def accepted_entry_count(self) -> int:
        return sum(entry.accepted for entry in self.entries)

    @property
    def rejected_entry_count(self) -> int:
        return sum(not entry.accepted for entry in self.entries)

    @property
    def repository_names(self) -> list[str]:
        return sorted(
            {
                entry.repository_name
                for entry in self.entries
            }
        )

    @property
    def latest_entry_hash(self) -> str:
        if not self.entries:
            return GENESIS_HASH

        return self.entries[-1].entry_hash

    @property
    def all_entries_accepted(self) -> bool:
        return (
            self.entry_count > 0
            and self.rejected_entry_count == 0
        )

    @property
    def status(self) -> str:
        if self.entry_count == 0:
            return "empty"

        if self.all_entries_accepted:
            return "accepted"

        return "contains_rejections"

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "entries": [
                {
                    **entry.canonical_payload(),
                    "entry_hash": entry.entry_hash,
                }
                for entry in self.entries
            ],
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        )

    def as_json(self) -> str:
        payload = self.canonical_payload()
        payload["ledger_id"] = self.ledger_id
        payload["status"] = self.status

        return json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ) + "\n"

    def as_markdown(self) -> str:
        lines = [
            "# Repository Release Audit Ledger",
            "",
            f"- **Ledger ID:** `{self.ledger_id}`",
            f"- **Entries:** {self.entry_count}",
            f"- **Accepted:** {self.accepted_entry_count}",
            f"- **Rejected:** {self.rejected_entry_count}",
            f"- **Status:** {self.status}",
            "",
            "## Entries",
            "",
        ]

        if not self.entries:
            lines.append("- No ledger entries.")

        for entry in self.entries:
            lines.append(
                f"- **{entry.sequence}. {entry.repository_name}** — "
                f"`{entry.bundle_id[:12]}` — "
                f"{'accepted' if entry.accepted else 'rejected'}"
            )

        return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerVerification:
    ledger_id: str
    integrity_valid: bool
    chain_valid: bool
    entry_count: int
    invalid_entry_sequences: list[int] = field(
        default_factory=list
    )

    @property
    def valid(self) -> bool:
        return (
            self.integrity_valid
            and self.chain_valid
            and not self.invalid_entry_sequences
        )


class RepositoryReleaseAuditLedgerBuilder:
    def build(
        self,
        bundle_json_values: list[str],
        require_accepted: bool = False,
    ) -> RepositoryReleaseAuditLedger:
        verifications = [
            RepositoryReleaseAuditBundleVerifier().verify_json(
                bundle_json=value,
                require_accepted=require_accepted,
            )
            for value in bundle_json_values
        ]

        return self.from_verifications(verifications)

    def from_verifications(
        self,
        verifications: list[
            RepositoryReleaseAuditBundleVerification
        ],
    ) -> RepositoryReleaseAuditLedger:
        entries: list[RepositoryReleaseAuditLedgerEntry] = []
        previous_hash = GENESIS_HASH

        for sequence, verification in enumerate(
            verifications,
            start=1,
        ):
            provisional = RepositoryReleaseAuditLedgerEntry(
                sequence=sequence,
                bundle_id=verification.bundle_id,
                repository_name=verification.repository_name,
                accepted=verification.accepted,
                previous_entry_hash=previous_hash,
                entry_hash="",
            )

            entry_hash = hashlib.sha256(
                provisional.canonical_json().encode("utf-8")
            ).hexdigest()

            entry = RepositoryReleaseAuditLedgerEntry(
                sequence=provisional.sequence,
                bundle_id=provisional.bundle_id,
                repository_name=provisional.repository_name,
                accepted=provisional.accepted,
                previous_entry_hash=provisional.previous_entry_hash,
                entry_hash=entry_hash,
            )

            entries.append(entry)
            previous_hash = entry_hash

        provisional_ledger = RepositoryReleaseAuditLedger(
            schema_version=RELEASE_AUDIT_LEDGER_SCHEMA_VERSION,
            ledger_id="",
            entries=entries,
        )

        ledger_id = hashlib.sha256(
            provisional_ledger.canonical_json().encode("utf-8")
        ).hexdigest()

        return RepositoryReleaseAuditLedger(
            schema_version=provisional_ledger.schema_version,
            ledger_id=ledger_id,
            entries=provisional_ledger.entries,
        )


class RepositoryReleaseAuditLedgerVerifier:
    def verify(
        self,
        ledger: RepositoryReleaseAuditLedger,
    ) -> RepositoryReleaseAuditLedgerVerification:
        expected_ledger_id = hashlib.sha256(
            ledger.canonical_json().encode("utf-8")
        ).hexdigest()

        invalid_sequences: list[int] = []
        previous_hash = GENESIS_HASH

        for expected_sequence, entry in enumerate(
            ledger.entries,
            start=1,
        ):
            if entry.sequence != expected_sequence:
                invalid_sequences.append(entry.sequence)

            if entry.previous_entry_hash != previous_hash:
                invalid_sequences.append(entry.sequence)

            expected_entry_hash = hashlib.sha256(
                entry.canonical_json().encode("utf-8")
            ).hexdigest()

            if entry.entry_hash != expected_entry_hash:
                invalid_sequences.append(entry.sequence)

            previous_hash = entry.entry_hash

        return RepositoryReleaseAuditLedgerVerification(
            ledger_id=ledger.ledger_id,
            integrity_valid=(
                ledger.ledger_id == expected_ledger_id
            ),
            chain_valid=not invalid_sequences,
            entry_count=ledger.entry_count,
            invalid_entry_sequences=sorted(
                set(invalid_sequences)
            ),
        )
