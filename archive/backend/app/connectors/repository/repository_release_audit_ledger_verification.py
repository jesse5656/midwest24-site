from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.connectors.repository.repository_release_audit_ledger import (
    GENESIS_HASH,
    RELEASE_AUDIT_LEDGER_SCHEMA_VERSION,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerVerificationIssue:
    code: str
    severity: str
    message: str
    sequence: int | None = None


@dataclass(frozen=True)
class RepositoryReleaseAuditLedgerDocumentVerification:
    ledger_id: str
    schema_version: str
    integrity_valid: bool
    chain_valid: bool
    entry_count: int
    accepted_entry_count: int
    rejected_entry_count: int
    issues: list[
        RepositoryReleaseAuditLedgerVerificationIssue
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
            and self.chain_valid
            and self.critical_issue_count == 0
            and self.error_issue_count == 0
        )

    @property
    def accepted(self) -> bool:
        return (
            self.valid
            and self.entry_count > 0
            and self.rejected_entry_count == 0
        )

    @property
    def rejected(self) -> bool:
        return not self.accepted

    @property
    def status(self) -> str:
        if self.accepted:
            return "release_audit_ledger_accepted"

        if self.critical_issue_count > 0:
            return "release_audit_ledger_rejected_critical"

        if not self.valid:
            return "release_audit_ledger_rejected"

        if self.entry_count == 0:
            return "release_audit_ledger_empty"

        return "release_audit_ledger_contains_rejections"


class RepositoryReleaseAuditLedgerDocumentVerifier:
    required_fields = {
        "schema_version",
        "ledger_id",
        "status",
        "entries",
    }

    entry_required_fields = {
        "sequence",
        "bundle_id",
        "repository_name",
        "accepted",
        "previous_entry_hash",
        "entry_hash",
    }

    def verify_json(
        self,
        ledger_json: str,
        require_all_accepted: bool = True,
        expected_ledger_id: str | None = None,
        expected_bundle_ids: list[str] | None = None,
    ) -> RepositoryReleaseAuditLedgerDocumentVerification:
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

        missing = sorted(
            self.required_fields - set(payload)
        )

        if missing:
            raise ValueError(
                "Release audit ledger is missing required field(s): "
                + ", ".join(missing)
            )

        return self.verify_payload(
            payload=payload,
            require_all_accepted=require_all_accepted,
            expected_ledger_id=expected_ledger_id,
            expected_bundle_ids=expected_bundle_ids,
        )

    def verify_payload(
        self,
        payload: dict[str, Any],
        require_all_accepted: bool = True,
        expected_ledger_id: str | None = None,
        expected_bundle_ids: list[str] | None = None,
    ) -> RepositoryReleaseAuditLedgerDocumentVerification:
        issues: list[
            RepositoryReleaseAuditLedgerVerificationIssue
        ] = []

        schema_version = str(
            payload.get("schema_version", "")
        )
        ledger_id = str(
            payload.get("ledger_id", "")
        )
        ledger_status = str(
            payload.get("status", "")
        )
        raw_entries = payload.get("entries", [])

        if schema_version != RELEASE_AUDIT_LEDGER_SCHEMA_VERSION:
            issues.append(
                RepositoryReleaseAuditLedgerVerificationIssue(
                    code="unsupported_schema_version",
                    severity="critical",
                    message=(
                        f"Audit ledger schema version "
                        f"{schema_version!r} is not supported."
                    ),
                )
            )

        if not self._is_sha256(ledger_id):
            issues.append(
                RepositoryReleaseAuditLedgerVerificationIssue(
                    code="invalid_ledger_id",
                    severity="critical",
                    message=(
                        "Ledger ID is not a valid SHA-256 digest."
                    ),
                )
            )

        if not isinstance(raw_entries, list):
            raise ValueError(
                "Release audit ledger entries must be a list."
            )

        normalized_entries: list[dict[str, Any]] = []
        previous_entry_hash = GENESIS_HASH
        accepted_entry_count = 0
        rejected_entry_count = 0

        for index, raw_entry in enumerate(
            raw_entries,
            start=1,
        ):
            if not isinstance(raw_entry, dict):
                issues.append(
                    RepositoryReleaseAuditLedgerVerificationIssue(
                        code="invalid_entry_type",
                        severity="critical",
                        message=(
                            f"Ledger entry {index} is not an object."
                        ),
                        sequence=index,
                    )
                )
                continue

            missing_entry_fields = sorted(
                self.entry_required_fields - set(raw_entry)
            )

            if missing_entry_fields:
                issues.append(
                    RepositoryReleaseAuditLedgerVerificationIssue(
                        code="missing_entry_fields",
                        severity="critical",
                        message=(
                            f"Ledger entry {index} is missing: "
                            + ", ".join(missing_entry_fields)
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
            stored_previous_hash = str(
                raw_entry["previous_entry_hash"]
            )
            entry_hash = str(raw_entry["entry_hash"])

            normalized_entry = {
                "sequence": sequence,
                "bundle_id": bundle_id,
                "repository_name": repository_name,
                "accepted": accepted,
                "previous_entry_hash": stored_previous_hash,
                "entry_hash": entry_hash,
            }

            normalized_entries.append(normalized_entry)

            if accepted:
                accepted_entry_count += 1
            else:
                rejected_entry_count += 1

            if sequence != index:
                issues.append(
                    RepositoryReleaseAuditLedgerVerificationIssue(
                        code="invalid_entry_sequence",
                        severity="critical",
                        message=(
                            f"Expected entry sequence {index}, "
                            f"received {sequence}."
                        ),
                        sequence=sequence,
                    )
                )

            if not self._is_sha256(bundle_id):
                issues.append(
                    RepositoryReleaseAuditLedgerVerificationIssue(
                        code="invalid_bundle_id",
                        severity="critical",
                        message=(
                            f"Entry {sequence} bundle ID is invalid."
                        ),
                        sequence=sequence,
                    )
                )

            if not repository_name.strip():
                issues.append(
                    RepositoryReleaseAuditLedgerVerificationIssue(
                        code="missing_repository_name",
                        severity="error",
                        message=(
                            f"Entry {sequence} repository name is empty."
                        ),
                        sequence=sequence,
                    )
                )

            if not self._is_sha256(stored_previous_hash):
                issues.append(
                    RepositoryReleaseAuditLedgerVerificationIssue(
                        code="invalid_previous_entry_hash",
                        severity="critical",
                        message=(
                            f"Entry {sequence} previous hash is invalid."
                        ),
                        sequence=sequence,
                    )
                )

            if not self._is_sha256(entry_hash):
                issues.append(
                    RepositoryReleaseAuditLedgerVerificationIssue(
                        code="invalid_entry_hash",
                        severity="critical",
                        message=(
                            f"Entry {sequence} hash is invalid."
                        ),
                        sequence=sequence,
                    )
                )

            if stored_previous_hash != previous_entry_hash:
                issues.append(
                    RepositoryReleaseAuditLedgerVerificationIssue(
                        code="broken_chain_link",
                        severity="critical",
                        message=(
                            f"Entry {sequence} does not reference "
                            "the preceding entry hash."
                        ),
                        sequence=sequence,
                    )
                )

            canonical_entry_payload = {
                "sequence": sequence,
                "bundle_id": bundle_id,
                "repository_name": repository_name,
                "accepted": accepted,
                "previous_entry_hash": stored_previous_hash,
            }

            expected_entry_hash = hashlib.sha256(
                json.dumps(
                    canonical_entry_payload,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()

            if entry_hash != expected_entry_hash:
                issues.append(
                    RepositoryReleaseAuditLedgerVerificationIssue(
                        code="entry_integrity_failure",
                        severity="critical",
                        message=(
                            f"Entry {sequence} hash does not match "
                            "its payload."
                        ),
                        sequence=sequence,
                    )
                )

            previous_entry_hash = entry_hash

        canonical_ledger_payload = {
            "schema_version": schema_version,
            "entries": normalized_entries,
        }

        expected_calculated_ledger_id = hashlib.sha256(
            json.dumps(
                canonical_ledger_payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        integrity_valid = (
            ledger_id == expected_calculated_ledger_id
        )

        if not integrity_valid:
            issues.append(
                RepositoryReleaseAuditLedgerVerificationIssue(
                    code="ledger_integrity_failure",
                    severity="critical",
                    message=(
                        "Ledger ID does not match the ledger payload."
                    ),
                )
            )

        chain_issue_codes = {
            "invalid_entry_sequence",
            "invalid_previous_entry_hash",
            "invalid_entry_hash",
            "broken_chain_link",
            "entry_integrity_failure",
            "missing_entry_fields",
            "invalid_entry_type",
        }

        chain_valid = not any(
            issue.code in chain_issue_codes
            for issue in issues
        )

        expected_status = self._expected_status(
            entry_count=len(normalized_entries),
            rejected_entry_count=rejected_entry_count,
        )

        if ledger_status != expected_status:
            issues.append(
                RepositoryReleaseAuditLedgerVerificationIssue(
                    code="inconsistent_ledger_status",
                    severity="error",
                    message=(
                        f"Ledger status {ledger_status!r} does not "
                        f"match calculated status {expected_status!r}."
                    ),
                )
            )

        if (
            require_all_accepted
            and rejected_entry_count > 0
        ):
            issues.append(
                RepositoryReleaseAuditLedgerVerificationIssue(
                    code="ledger_contains_rejections",
                    severity="error",
                    message=(
                        "All ledger entries must be accepted."
                    ),
                )
            )

        if (
            require_all_accepted
            and len(normalized_entries) == 0
        ):
            issues.append(
                RepositoryReleaseAuditLedgerVerificationIssue(
                    code="ledger_empty",
                    severity="error",
                    message=(
                        "An accepted ledger must contain at least "
                        "one entry."
                    ),
                )
            )

        if (
            expected_ledger_id is not None
            and ledger_id != expected_ledger_id
        ):
            issues.append(
                RepositoryReleaseAuditLedgerVerificationIssue(
                    code="ledger_id_mismatch",
                    severity="critical",
                    message=(
                        "Ledger ID does not match the expected value."
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
                    RepositoryReleaseAuditLedgerVerificationIssue(
                        code="bundle_sequence_mismatch",
                        severity="critical",
                        message=(
                            "Ledger bundle sequence does not match "
                            "the expected bundle sequence."
                        ),
                    )
                )

        return RepositoryReleaseAuditLedgerDocumentVerification(
            ledger_id=ledger_id,
            schema_version=schema_version,
            integrity_valid=integrity_valid,
            chain_valid=chain_valid,
            entry_count=len(normalized_entries),
            accepted_entry_count=accepted_entry_count,
            rejected_entry_count=rejected_entry_count,
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
        entry_count: int,
        rejected_entry_count: int,
    ) -> str:
        if entry_count == 0:
            return "empty"

        if rejected_entry_count == 0:
            return "accepted"

        return "contains_rejections"

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
