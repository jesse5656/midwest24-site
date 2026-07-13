from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.connectors.repository.repository_release_audit_ledger import (
    GENESIS_HASH,
)
from app.connectors.repository.repository_release_audit_ledger_snapshot import (
    RELEASE_AUDIT_LEDGER_SNAPSHOT_SCHEMA_VERSION,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerSnapshotVerificationIssue:
    code: str
    severity: str
    message: str
    sequence: int | None = None


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerSnapshotVerification:
    snapshot_id: str
    ledger_id: str
    schema_version: str
    snapshot_accepted: bool
    integrity_valid: bool
    entry_count: int
    accepted_entry_count: int
    rejected_entry_count: int
    repository_count: int
    issues: list[
        RepositoryReleaseAuditLedgerSnapshotVerificationIssue
    ] = field(default_factory=list)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def critical_issue_count(self) -> int:
        return sum(
            issue.severity == "critical"
            for issue in self.issues
        )

    @property
    def error_issue_count(self) -> int:
        return sum(
            issue.severity == "error"
            for issue in self.issues
        )

    @property
    def warning_issue_count(self) -> int:
        return sum(
            issue.severity == "warning"
            for issue in self.issues
        )

    @property
    def issue_codes(self) -> list[str]:
        return sorted(
            {
                issue.code
                for issue in self.issues
            }
        )

    @property
    def invalid_entry_sequences(self) -> list[int]:
        return sorted(
            {
                issue.sequence
                for issue in self.issues
                if issue.sequence is not None
            }
        )

    @property
    def valid(self) -> bool:
        return (
            self.integrity_valid
            and self.critical_issue_count == 0
            and self.error_issue_count == 0
        )

    @property
    def accepted(self) -> bool:
        return self.valid and self.snapshot_accepted

    @property
    def rejected(self) -> bool:
        return not self.accepted

    @property
    def status(self) -> str:
        if self.accepted:
            return "ledger_snapshot_accepted"

        if self.critical_issue_count > 0:
            return "ledger_snapshot_rejected_critical"

        if not self.valid:
            return "ledger_snapshot_rejected"

        return "ledger_snapshot_valid_not_accepted"


class RepositoryReleaseAuditLedgerSnapshotVerifier:
    required_fields = {
        "schema_version",
        "snapshot_id",
        "ledger_id",
        "ledger_integrity_valid",
        "ledger_chain_valid",
        "ledger_accepted",
        "accepted",
        "status",
        "entry_count",
        "accepted_entry_count",
        "rejected_entry_count",
        "latest_entry_hash",
        "repository_names",
        "entries",
        "issue_codes",
    }

    entry_required_fields = {
        "sequence",
        "bundle_id",
        "repository_name",
        "accepted",
        "entry_hash",
    }

    def verify_json(
        self,
        snapshot_json: str,
        require_accepted: bool = True,
        expected_snapshot_id: str | None = None,
        expected_ledger_id: str | None = None,
        expected_latest_entry_hash: str | None = None,
        expected_bundle_ids: list[str] | None = None,
    ) -> RepositoryReleaseAuditLedgerSnapshotVerification:
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

        missing = sorted(
            self.required_fields - set(payload)
        )

        if missing:
            raise ValueError(
                "Ledger snapshot is missing required field(s): "
                + ", ".join(missing)
            )

        return self.verify_payload(
            payload=payload,
            require_accepted=require_accepted,
            expected_snapshot_id=expected_snapshot_id,
            expected_ledger_id=expected_ledger_id,
            expected_latest_entry_hash=(
                expected_latest_entry_hash
            ),
            expected_bundle_ids=expected_bundle_ids,
        )

    def verify_payload(
        self,
        payload: dict[str, Any],
        require_accepted: bool = True,
        expected_snapshot_id: str | None = None,
        expected_ledger_id: str | None = None,
        expected_latest_entry_hash: str | None = None,
        expected_bundle_ids: list[str] | None = None,
    ) -> RepositoryReleaseAuditLedgerSnapshotVerification:
        issues: list[
            RepositoryReleaseAuditLedgerSnapshotVerificationIssue
        ] = []

        schema_version = str(
            payload.get("schema_version", "")
        )
        snapshot_id = str(
            payload.get("snapshot_id", "")
        )
        ledger_id = str(
            payload.get("ledger_id", "")
        )
        ledger_integrity_valid = bool(
            payload.get("ledger_integrity_valid", False)
        )
        ledger_chain_valid = bool(
            payload.get("ledger_chain_valid", False)
        )
        ledger_accepted = bool(
            payload.get("ledger_accepted", False)
        )
        snapshot_accepted = bool(
            payload.get("accepted", False)
        )
        snapshot_status = str(
            payload.get("status", "")
        )
        stored_entry_count = int(
            payload.get("entry_count", 0)
        )
        stored_accepted_count = int(
            payload.get("accepted_entry_count", 0)
        )
        stored_rejected_count = int(
            payload.get("rejected_entry_count", 0)
        )
        latest_entry_hash = str(
            payload.get("latest_entry_hash", "")
        )
        repository_names = payload.get(
            "repository_names",
            [],
        )
        raw_entries = payload.get("entries", [])
        stored_issue_codes = payload.get(
            "issue_codes",
            [],
        )

        if schema_version != (
            RELEASE_AUDIT_LEDGER_SNAPSHOT_SCHEMA_VERSION
        ):
            issues.append(
                RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                    code="unsupported_schema_version",
                    severity="critical",
                    message=(
                        f"Ledger snapshot schema version "
                        f"{schema_version!r} is not supported."
                    ),
                )
            )

        for name, value in {
            "snapshot_id": snapshot_id,
            "ledger_id": ledger_id,
            "latest_entry_hash": latest_entry_hash,
        }.items():
            if not self._is_sha256(value):
                issues.append(
                    RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                        code=f"invalid_{name}",
                        severity="critical",
                        message=(
                            f"{name} is not a valid SHA-256 digest."
                        ),
                    )
                )

        if not isinstance(repository_names, list):
            raise ValueError(
                "Ledger snapshot repository_names must be a list."
            )

        if not isinstance(raw_entries, list):
            raise ValueError(
                "Ledger snapshot entries must be a list."
            )

        if not isinstance(stored_issue_codes, list):
            raise ValueError(
                "Ledger snapshot issue_codes must be a list."
            )

        normalized_entries: list[dict[str, Any]] = []
        actual_repository_names: set[str] = set()
        accepted_count = 0
        rejected_count = 0

        for index, raw_entry in enumerate(
            raw_entries,
            start=1,
        ):
            if not isinstance(raw_entry, dict):
                issues.append(
                    RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                        code="invalid_entry_type",
                        severity="critical",
                        message=(
                            f"Snapshot entry {index} is not an object."
                        ),
                        sequence=index,
                    )
                )
                continue

            missing = sorted(
                self.entry_required_fields - set(raw_entry)
            )

            if missing:
                issues.append(
                    RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                        code="missing_entry_fields",
                        severity="critical",
                        message=(
                            f"Snapshot entry {index} is missing: "
                            + ", ".join(missing)
                        ),
                        sequence=index,
                    )
                )
                continue

            sequence = int(raw_entry["sequence"])
            bundle_id = str(raw_entry["bundle_id"])
            repository_name = str(
                raw_entry["repository_name"]
            )
            accepted = bool(raw_entry["accepted"])
            entry_hash = str(raw_entry["entry_hash"])

            normalized_entries.append(
                {
                    "sequence": sequence,
                    "bundle_id": bundle_id,
                    "repository_name": repository_name,
                    "accepted": accepted,
                    "entry_hash": entry_hash,
                }
            )

            if accepted:
                accepted_count += 1
            else:
                rejected_count += 1

            if repository_name:
                actual_repository_names.add(repository_name)

            if sequence != index:
                issues.append(
                    RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                        code="invalid_entry_sequence",
                        severity="critical",
                        message=(
                            f"Expected sequence {index}, "
                            f"received {sequence}."
                        ),
                        sequence=sequence,
                    )
                )

            if not self._is_sha256(bundle_id):
                issues.append(
                    RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                        code="invalid_bundle_id",
                        severity="critical",
                        message=(
                            f"Entry {sequence} bundle ID is invalid."
                        ),
                        sequence=sequence,
                    )
                )

            if not self._is_sha256(entry_hash):
                issues.append(
                    RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                        code="invalid_entry_hash",
                        severity="critical",
                        message=(
                            f"Entry {sequence} hash is invalid."
                        ),
                        sequence=sequence,
                    )
                )

            if not repository_name.strip():
                issues.append(
                    RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                        code="missing_repository_name",
                        severity="error",
                        message=(
                            f"Entry {sequence} repository name is empty."
                        ),
                        sequence=sequence,
                    )
                )

        actual_entry_count = len(normalized_entries)

        if stored_entry_count != actual_entry_count:
            issues.append(
                RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                    code="entry_count_mismatch",
                    severity="error",
                    message=(
                        f"Stored entry count {stored_entry_count} "
                        f"does not match calculated count "
                        f"{actual_entry_count}."
                    ),
                )
            )

        if stored_accepted_count != accepted_count:
            issues.append(
                RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                    code="accepted_count_mismatch",
                    severity="error",
                    message=(
                        "Stored accepted-entry count does not match "
                        "the snapshot entries."
                    ),
                )
            )

        if stored_rejected_count != rejected_count:
            issues.append(
                RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                    code="rejected_count_mismatch",
                    severity="error",
                    message=(
                        "Stored rejected-entry count does not match "
                        "the snapshot entries."
                    ),
                )
            )

        normalized_repository_names = sorted(
            str(name)
            for name in repository_names
        )
        calculated_repository_names = sorted(
            actual_repository_names
        )

        if (
            normalized_repository_names
            != calculated_repository_names
        ):
            issues.append(
                RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                    code="repository_names_mismatch",
                    severity="error",
                    message=(
                        "Stored repository names do not match "
                        "the snapshot entries."
                    ),
                )
            )

        calculated_latest_hash = (
            normalized_entries[-1]["entry_hash"]
            if normalized_entries
            else GENESIS_HASH
        )

        if latest_entry_hash != calculated_latest_hash:
            issues.append(
                RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                    code="latest_entry_hash_mismatch",
                    severity="critical",
                    message=(
                        "Latest entry hash does not match the "
                        "final snapshot entry."
                    ),
                )
            )

        normalized_issue_codes = sorted(
            str(code)
            for code in stored_issue_codes
        )

        canonical_payload = {
            "schema_version": schema_version,
            "ledger_id": ledger_id,
            "ledger_integrity_valid": (
                ledger_integrity_valid
            ),
            "ledger_chain_valid": ledger_chain_valid,
            "ledger_accepted": ledger_accepted,
            "entry_count": stored_entry_count,
            "accepted_entry_count": (
                stored_accepted_count
            ),
            "rejected_entry_count": (
                stored_rejected_count
            ),
            "latest_entry_hash": latest_entry_hash,
            "repository_names": (
                normalized_repository_names
            ),
            "entries": sorted(
                normalized_entries,
                key=lambda entry: entry["sequence"],
            ),
            "issue_codes": normalized_issue_codes,
        }

        expected_snapshot_digest = hashlib.sha256(
            json.dumps(
                canonical_payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        integrity_valid = (
            snapshot_id == expected_snapshot_digest
        )

        if not integrity_valid:
            issues.append(
                RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                    code="snapshot_integrity_failure",
                    severity="critical",
                    message=(
                        "Snapshot ID does not match the "
                        "snapshot payload."
                    ),
                )
            )

        calculated_accepted = (
            ledger_integrity_valid
            and ledger_chain_valid
            and ledger_accepted
            and rejected_count == 0
            and len(normalized_issue_codes) == 0
        )

        if snapshot_accepted != calculated_accepted:
            issues.append(
                RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                    code="inconsistent_acceptance_state",
                    severity="error",
                    message=(
                        "Stored snapshot acceptance state does not "
                        "match calculated state."
                    ),
                )
            )

        expected_status = self._expected_status(
            accepted=calculated_accepted,
            ledger_integrity_valid=ledger_integrity_valid,
            ledger_chain_valid=ledger_chain_valid,
        )

        if snapshot_status != expected_status:
            issues.append(
                RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                    code="inconsistent_snapshot_status",
                    severity="error",
                    message=(
                        f"Snapshot status {snapshot_status!r} does "
                        f"not match calculated status "
                        f"{expected_status!r}."
                    ),
                )
            )

        if require_accepted and not snapshot_accepted:
            issues.append(
                RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                    code="snapshot_not_accepted",
                    severity="error",
                    message=(
                        "An accepted ledger snapshot is required."
                    ),
                )
            )

        expectations = {
            "snapshot_id_mismatch": (
                expected_snapshot_id,
                snapshot_id,
            ),
            "ledger_id_mismatch": (
                expected_ledger_id,
                ledger_id,
            ),
            "latest_entry_hash_expected_mismatch": (
                expected_latest_entry_hash,
                latest_entry_hash,
            ),
        }

        for code, values in expectations.items():
            expected, actual = values

            if expected is not None and expected != actual:
                issues.append(
                    RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                        code=code,
                        severity="critical",
                        message=(
                            "Snapshot identifier does not match "
                            "the expected value."
                        ),
                    )
                )

        if expected_bundle_ids is not None:
            actual_bundle_ids = [
                entry["bundle_id"]
                for entry in normalized_entries
            ]

            if actual_bundle_ids != expected_bundle_ids:
                issues.append(
                    RepositoryReleaseAuditLedgerSnapshotVerificationIssue(
                        code="bundle_sequence_mismatch",
                        severity="critical",
                        message=(
                            "Snapshot bundle sequence does not match "
                            "the expected sequence."
                        ),
                    )
                )

        return RepositoryReleaseAuditLedgerSnapshotVerification(
            snapshot_id=snapshot_id,
            ledger_id=ledger_id,
            schema_version=schema_version,
            snapshot_accepted=snapshot_accepted,
            integrity_valid=integrity_valid,
            entry_count=actual_entry_count,
            accepted_entry_count=accepted_count,
            rejected_entry_count=rejected_count,
            repository_count=len(
                calculated_repository_names
            ),
            issues=sorted(
                issues,
                key=lambda issue: (
                    0 if issue.severity == "critical" else 1,
                    issue.sequence
                    if issue.sequence is not None
                    else 0,
                    issue.code,
                    issue.message,
                ),
            ),
        )

    def _expected_status(
        self,
        accepted: bool,
        ledger_integrity_valid: bool,
        ledger_chain_valid: bool,
    ) -> str:
        if accepted:
            return "ledger_snapshot_accepted"

        if not ledger_integrity_valid:
            return "ledger_snapshot_invalid_integrity"

        if not ledger_chain_valid:
            return "ledger_snapshot_invalid_chain"

        return "ledger_snapshot_rejected"

    def _is_sha256(
        self,
        value: str,
    ) -> bool:
        if len(value) != 64:
            return False

        try:
            int(value, 16)
        except ValueError:
            return False

        return True
