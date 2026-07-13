from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.connectors.repository.repository_release_attestation import (
    ATTESTATION_SCHEMA_VERSION,
)


@dataclass(frozen=True)
class RepositoryReleaseAttestationVerificationIssue:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class RepositoryReleaseAttestationVerification:
    attestation_id: str
    certificate_id: str
    repository_name: str
    schema_version: str
    certified: bool
    certificate_valid: bool
    integrity_valid: bool
    issues: list[
        RepositoryReleaseAttestationVerificationIssue
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
    def valid(self) -> bool:
        return (
            self.integrity_valid
            and self.critical_issue_count == 0
            and self.error_issue_count == 0
        )

    @property
    def accepted(self) -> bool:
        return (
            self.valid
            and self.certified
            and self.certificate_valid
        )

    @property
    def rejected(self) -> bool:
        return not self.accepted

    @property
    def status(self) -> str:
        if self.accepted:
            return "attestation_accepted"

        if self.critical_issue_count > 0:
            return "attestation_rejected_critical"

        if not self.valid:
            return "attestation_rejected"

        return "attestation_valid_not_accepted"


class RepositoryReleaseAttestationVerifier:
    required_fields = {
        "schema_version",
        "repository_name",
        "attestation_id",
        "certificate_id",
        "certificate_valid",
        "certified",
        "baseline_fingerprint",
        "candidate_fingerprint",
        "evidence",
        "issues",
    }

    def verify_json(
        self,
        attestation_json: str,
        require_accepted: bool = True,
        expected_certificate_id: str | None = None,
        expected_baseline_fingerprint: str | None = None,
        expected_candidate_fingerprint: str | None = None,
    ) -> RepositoryReleaseAttestationVerification:
        try:
            payload = json.loads(attestation_json)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid release attestation JSON: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "Release attestation JSON must contain an object."
            )

        missing = sorted(
            self.required_fields - set(payload)
        )

        if missing:
            raise ValueError(
                "Release attestation is missing required field(s): "
                + ", ".join(missing)
            )

        return self.verify_payload(
            payload=payload,
            require_accepted=require_accepted,
            expected_certificate_id=expected_certificate_id,
            expected_baseline_fingerprint=(
                expected_baseline_fingerprint
            ),
            expected_candidate_fingerprint=(
                expected_candidate_fingerprint
            ),
        )

    def verify_payload(
        self,
        payload: dict[str, Any],
        require_accepted: bool = True,
        expected_certificate_id: str | None = None,
        expected_baseline_fingerprint: str | None = None,
        expected_candidate_fingerprint: str | None = None,
    ) -> RepositoryReleaseAttestationVerification:
        issues: list[
            RepositoryReleaseAttestationVerificationIssue
        ] = []

        schema_version = str(
            payload.get("schema_version", "")
        )
        repository_name = str(
            payload.get("repository_name", "")
        )
        attestation_id = str(
            payload.get("attestation_id", "")
        )
        certificate_id = str(
            payload.get("certificate_id", "")
        )
        certificate_valid = bool(
            payload.get("certificate_valid", False)
        )
        certified = bool(
            payload.get("certified", False)
        )
        baseline_fingerprint = str(
            payload.get("baseline_fingerprint", "")
        )
        candidate_fingerprint = str(
            payload.get("candidate_fingerprint", "")
        )
        evidence = payload.get("evidence", [])
        attestation_issues = payload.get("issues", [])

        if schema_version != ATTESTATION_SCHEMA_VERSION:
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="unsupported_schema_version",
                    severity="critical",
                    message=(
                        f"Attestation schema version "
                        f"{schema_version!r} is not supported."
                    ),
                )
            )

        if not repository_name.strip():
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="missing_repository_name",
                    severity="error",
                    message="Attestation repository name is empty.",
                )
            )

        if not self._is_sha256(attestation_id):
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="invalid_attestation_id",
                    severity="critical",
                    message=(
                        "Attestation ID is not a valid SHA-256 digest."
                    ),
                )
            )

        if not self._is_sha256(certificate_id):
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="invalid_certificate_id",
                    severity="critical",
                    message=(
                        "Certificate ID is not a valid SHA-256 digest."
                    ),
                )
            )

        canonical_payload = {
            "schema_version": schema_version,
            "repository_name": repository_name,
            "certificate_id": certificate_id,
            "certificate_valid": certificate_valid,
            "certified": certified,
            "baseline_fingerprint": baseline_fingerprint,
            "candidate_fingerprint": candidate_fingerprint,
            "evidence": self._normalize_evidence(evidence),
            "issues": sorted(
                str(issue)
                for issue in attestation_issues
            ),
        }

        expected_attestation_id = hashlib.sha256(
            json.dumps(
                canonical_payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        integrity_valid = (
            attestation_id == expected_attestation_id
        )

        if not integrity_valid:
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="attestation_integrity_failure",
                    severity="critical",
                    message=(
                        "Attestation ID does not match the "
                        "attestation payload."
                    ),
                )
            )

        failed_evidence = [
            item
            for item in evidence
            if isinstance(item, dict)
            and not bool(item.get("passed", False))
        ]

        if certified and failed_evidence:
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="certified_with_failed_evidence",
                    severity="critical",
                    message=(
                        "Certified attestation contains failed "
                        "evidence items."
                    ),
                )
            )

        if certified and not certificate_valid:
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="certified_with_invalid_certificate",
                    severity="critical",
                    message=(
                        "Certified attestation references an "
                        "invalid certificate."
                    ),
                )
            )

        if certified and attestation_issues:
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="certified_with_attestation_issues",
                    severity="error",
                    message=(
                        "Certified attestation contains unresolved "
                        "verification issues."
                    ),
                )
            )

        accepted = (
            certified
            and certificate_valid
            and not failed_evidence
            and not attestation_issues
        )

        if require_accepted and not accepted:
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="attestation_not_accepted",
                    severity="error",
                    message=(
                        "An accepted release attestation is required."
                    ),
                )
            )

        if (
            expected_certificate_id is not None
            and certificate_id != expected_certificate_id
        ):
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="certificate_id_mismatch",
                    severity="critical",
                    message=(
                        "Attestation certificate ID does not match "
                        "the expected certificate ID."
                    ),
                )
            )

        if (
            expected_baseline_fingerprint is not None
            and baseline_fingerprint
            != expected_baseline_fingerprint
        ):
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="baseline_fingerprint_mismatch",
                    severity="critical",
                    message=(
                        "Attestation baseline fingerprint does not "
                        "match the expected fingerprint."
                    ),
                )
            )

        if (
            expected_candidate_fingerprint is not None
            and candidate_fingerprint
            != expected_candidate_fingerprint
        ):
            issues.append(
                RepositoryReleaseAttestationVerificationIssue(
                    code="candidate_fingerprint_mismatch",
                    severity="critical",
                    message=(
                        "Attestation candidate fingerprint does not "
                        "match the expected fingerprint."
                    ),
                )
            )

        return RepositoryReleaseAttestationVerification(
            attestation_id=attestation_id,
            certificate_id=certificate_id,
            repository_name=repository_name,
            schema_version=schema_version,
            certified=certified,
            certificate_valid=certificate_valid,
            integrity_valid=integrity_valid,
            issues=sorted(
                issues,
                key=lambda issue: (
                    0 if issue.severity == "critical" else 1,
                    issue.code,
                    issue.message,
                ),
            ),
        )

    def _normalize_evidence(
        self,
        evidence: Any,
    ) -> list[dict[str, Any]]:
        if not isinstance(evidence, list):
            return []

        normalized = []

        for item in evidence:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "name": str(item.get("name", "")),
                    "passed": bool(
                        item.get("passed", False)
                    ),
                    "severity": str(
                        item.get("severity", "")
                    ),
                    "message": str(
                        item.get("message", "")
                    ),
                }
            )

        return sorted(
            normalized,
            key=lambda item: item["name"],
        )

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
