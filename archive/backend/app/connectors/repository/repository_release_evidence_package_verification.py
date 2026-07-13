from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.connectors.repository.repository_release_evidence_package import (
    RELEASE_EVIDENCE_PACKAGE_SCHEMA_VERSION,
)


@dataclass(frozen=True)
class RepositoryReleaseEvidencePackageVerificationIssue:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class RepositoryReleaseEvidencePackageVerification:
    package_id: str
    repository_name: str
    schema_version: str
    certificate_id: str
    attestation_id: str
    integrity_valid: bool
    package_accepted: bool
    issues: list[
        RepositoryReleaseEvidencePackageVerificationIssue
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
        return self.valid and self.package_accepted

    @property
    def rejected(self) -> bool:
        return not self.accepted

    @property
    def status(self) -> str:
        if self.accepted:
            return "release_package_accepted"

        if self.critical_issue_count > 0:
            return "release_package_rejected_critical"

        if not self.valid:
            return "release_package_rejected"

        return "release_package_valid_not_accepted"


class RepositoryReleaseEvidencePackageVerifier:
    required_fields = {
        "schema_version",
        "repository_name",
        "package_id",
        "accepted",
        "status",
        "certificate_id",
        "certificate_accepted",
        "attestation_id",
        "attestation_accepted",
        "baseline_fingerprint",
        "candidate_fingerprint",
        "evidence",
    }

    def verify_json(
        self,
        package_json: str,
        require_accepted: bool = True,
        expected_certificate_id: str | None = None,
        expected_attestation_id: str | None = None,
        expected_baseline_fingerprint: str | None = None,
        expected_candidate_fingerprint: str | None = None,
    ) -> RepositoryReleaseEvidencePackageVerification:
        try:
            payload = json.loads(package_json)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid release evidence package JSON: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "Release evidence package JSON must contain an object."
            )

        missing = sorted(
            self.required_fields - set(payload)
        )

        if missing:
            raise ValueError(
                "Release evidence package is missing required field(s): "
                + ", ".join(missing)
            )

        return self.verify_payload(
            payload=payload,
            require_accepted=require_accepted,
            expected_certificate_id=expected_certificate_id,
            expected_attestation_id=expected_attestation_id,
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
        expected_attestation_id: str | None = None,
        expected_baseline_fingerprint: str | None = None,
        expected_candidate_fingerprint: str | None = None,
    ) -> RepositoryReleaseEvidencePackageVerification:
        issues: list[
            RepositoryReleaseEvidencePackageVerificationIssue
        ] = []

        schema_version = str(
            payload.get("schema_version", "")
        )
        repository_name = str(
            payload.get("repository_name", "")
        )
        package_id = str(
            payload.get("package_id", "")
        )
        package_accepted = bool(
            payload.get("accepted", False)
        )
        package_status = str(
            payload.get("status", "")
        )
        certificate_id = str(
            payload.get("certificate_id", "")
        )
        certificate_accepted = bool(
            payload.get("certificate_accepted", False)
        )
        attestation_id = str(
            payload.get("attestation_id", "")
        )
        attestation_accepted = bool(
            payload.get("attestation_accepted", False)
        )
        baseline_fingerprint = str(
            payload.get("baseline_fingerprint", "")
        )
        candidate_fingerprint = str(
            payload.get("candidate_fingerprint", "")
        )
        evidence = payload.get("evidence", [])

        if schema_version != RELEASE_EVIDENCE_PACKAGE_SCHEMA_VERSION:
            issues.append(
                RepositoryReleaseEvidencePackageVerificationIssue(
                    code="unsupported_schema_version",
                    severity="critical",
                    message=(
                        f"Evidence package schema version "
                        f"{schema_version!r} is not supported."
                    ),
                )
            )

        if not repository_name.strip():
            issues.append(
                RepositoryReleaseEvidencePackageVerificationIssue(
                    code="missing_repository_name",
                    severity="error",
                    message=(
                        "Evidence package repository name is empty."
                    ),
                )
            )

        for name, value in {
            "package_id": package_id,
            "certificate_id": certificate_id,
            "attestation_id": attestation_id,
            "baseline_fingerprint": baseline_fingerprint,
            "candidate_fingerprint": candidate_fingerprint,
        }.items():
            if not self._is_sha256(value):
                issues.append(
                    RepositoryReleaseEvidencePackageVerificationIssue(
                        code=f"invalid_{name}",
                        severity="critical",
                        message=(
                            f"{name} is not a valid SHA-256 digest."
                        ),
                    )
                )

        normalized_evidence = self._normalize_evidence(
            evidence
        )

        canonical_payload = {
            "schema_version": schema_version,
            "repository_name": repository_name,
            "certificate_id": certificate_id,
            "certificate_accepted": certificate_accepted,
            "attestation_id": attestation_id,
            "attestation_accepted": attestation_accepted,
            "baseline_fingerprint": baseline_fingerprint,
            "candidate_fingerprint": candidate_fingerprint,
            "evidence": normalized_evidence,
        }

        expected_package_id = hashlib.sha256(
            json.dumps(
                canonical_payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        integrity_valid = package_id == expected_package_id

        if not integrity_valid:
            issues.append(
                RepositoryReleaseEvidencePackageVerificationIssue(
                    code="package_integrity_failure",
                    severity="critical",
                    message=(
                        "Package ID does not match the package payload."
                    ),
                )
            )

        expected_status = (
            "release_package_accepted"
            if package_accepted
            else "release_package_rejected"
        )

        if package_status != expected_status:
            issues.append(
                RepositoryReleaseEvidencePackageVerificationIssue(
                    code="inconsistent_package_status",
                    severity="error",
                    message=(
                        f"Package status {package_status!r} does not "
                        f"match accepted state {package_accepted}."
                    ),
                )
            )

        rejected_evidence = [
            item
            for item in normalized_evidence
            if item["status"] == "rejected"
        ]

        if package_accepted and not certificate_accepted:
            issues.append(
                RepositoryReleaseEvidencePackageVerificationIssue(
                    code="accepted_with_rejected_certificate",
                    severity="critical",
                    message=(
                        "Accepted package contains a rejected "
                        "certificate."
                    ),
                )
            )

        if package_accepted and not attestation_accepted:
            issues.append(
                RepositoryReleaseEvidencePackageVerificationIssue(
                    code="accepted_with_rejected_attestation",
                    severity="critical",
                    message=(
                        "Accepted package contains a rejected "
                        "attestation."
                    ),
                )
            )

        if package_accepted and rejected_evidence:
            issues.append(
                RepositoryReleaseEvidencePackageVerificationIssue(
                    code="accepted_with_rejected_evidence",
                    severity="critical",
                    message=(
                        "Accepted package contains rejected evidence."
                    ),
                )
            )

        if require_accepted and not package_accepted:
            issues.append(
                RepositoryReleaseEvidencePackageVerificationIssue(
                    code="package_not_accepted",
                    severity="error",
                    message=(
                        "An accepted release evidence package is required."
                    ),
                )
            )

        expectations = {
            "certificate_id_mismatch": (
                expected_certificate_id,
                certificate_id,
                "certificate ID",
            ),
            "attestation_id_mismatch": (
                expected_attestation_id,
                attestation_id,
                "attestation ID",
            ),
            "baseline_fingerprint_mismatch": (
                expected_baseline_fingerprint,
                baseline_fingerprint,
                "baseline fingerprint",
            ),
            "candidate_fingerprint_mismatch": (
                expected_candidate_fingerprint,
                candidate_fingerprint,
                "candidate fingerprint",
            ),
        }

        for code, values in expectations.items():
            expected, actual, label = values

            if expected is not None and actual != expected:
                issues.append(
                    RepositoryReleaseEvidencePackageVerificationIssue(
                        code=code,
                        severity="critical",
                        message=(
                            f"Package {label} does not match "
                            f"the expected value."
                        ),
                    )
                )

        return RepositoryReleaseEvidencePackageVerification(
            package_id=package_id,
            repository_name=repository_name,
            schema_version=schema_version,
            certificate_id=certificate_id,
            attestation_id=attestation_id,
            integrity_valid=integrity_valid,
            package_accepted=package_accepted,
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
    ) -> list[dict[str, str]]:
        if not isinstance(evidence, list):
            return []

        normalized = []

        for item in evidence:
            if not isinstance(item, dict):
                continue

            normalized.append(
                {
                    "name": str(item.get("name", "")),
                    "status": str(item.get("status", "")),
                    "reference": str(
                        item.get("reference", "")
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
