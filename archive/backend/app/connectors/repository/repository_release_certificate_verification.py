from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.connectors.repository.repository_release_certification import (
    CERTIFICATION_SCHEMA_VERSION,
)


@dataclass(frozen=True)
class RepositoryReleaseCertificateVerificationIssue:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class RepositoryReleaseCertificateVerification:
    certificate_id: str
    repository_name: str
    schema_version: str
    certified: bool
    integrity_valid: bool
    issues: list[
        RepositoryReleaseCertificateVerificationIssue
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
        return self.valid and self.certified

    @property
    def status(self) -> str:
        if self.accepted:
            return "certificate_accepted"

        if self.critical_issue_count > 0:
            return "certificate_rejected_critical"

        if not self.valid:
            return "certificate_rejected"

        return "certificate_valid_not_certified"


class RepositoryReleaseCertificateVerifier:
    required_fields = {
        "schema_version",
        "repository_name",
        "release_ready",
        "status",
        "certificate_id",
        "baseline_fingerprint",
        "candidate_fingerprint",
        "evidence",
        "denial_reasons",
    }

    def verify_json(
        self,
        certificate_json: str,
        require_certified: bool = True,
        expected_baseline_fingerprint: str | None = None,
        expected_candidate_fingerprint: str | None = None,
    ) -> RepositoryReleaseCertificateVerification:
        try:
            payload = json.loads(certificate_json)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid release certificate JSON: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "Release certificate JSON must contain an object."
            )

        missing = sorted(
            self.required_fields - set(payload)
        )

        if missing:
            raise ValueError(
                "Release certificate is missing required field(s): "
                + ", ".join(missing)
            )

        return self.verify_payload(
            payload=payload,
            require_certified=require_certified,
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
        require_certified: bool = True,
        expected_baseline_fingerprint: str | None = None,
        expected_candidate_fingerprint: str | None = None,
    ) -> RepositoryReleaseCertificateVerification:
        issues: list[
            RepositoryReleaseCertificateVerificationIssue
        ] = []

        schema_version = str(
            payload.get("schema_version", "")
        )
        repository_name = str(
            payload.get("repository_name", "")
        )
        certificate_id = str(
            payload.get("certificate_id", "")
        )
        release_ready = bool(
            payload.get("release_ready", False)
        )
        certificate_status = str(
            payload.get("status", "")
        )
        baseline_fingerprint = str(
            payload.get("baseline_fingerprint", "")
        )
        candidate_fingerprint = str(
            payload.get("candidate_fingerprint", "")
        )
        denial_reasons = payload.get(
            "denial_reasons",
            [],
        )
        evidence = payload.get(
            "evidence",
            [],
        )

        if schema_version != CERTIFICATION_SCHEMA_VERSION:
            issues.append(
                RepositoryReleaseCertificateVerificationIssue(
                    code="unsupported_schema_version",
                    severity="critical",
                    message=(
                        f"Certificate schema version "
                        f"{schema_version!r} is not supported."
                    ),
                )
            )

        if not repository_name.strip():
            issues.append(
                RepositoryReleaseCertificateVerificationIssue(
                    code="missing_repository_name",
                    severity="error",
                    message=(
                        "Certificate repository name is empty."
                    ),
                )
            )

        if not self._is_sha256(certificate_id):
            issues.append(
                RepositoryReleaseCertificateVerificationIssue(
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
            "release_ready": release_ready,
            "status": certificate_status,
            "baseline_fingerprint": baseline_fingerprint,
            "candidate_fingerprint": candidate_fingerprint,
            "evidence": self._normalize_evidence(evidence),
            "denial_reasons": sorted(
                str(reason)
                for reason in denial_reasons
            ),
        }

        expected_certificate_id = hashlib.sha256(
            json.dumps(
                canonical_payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        integrity_valid = (
            certificate_id == expected_certificate_id
        )

        if not integrity_valid:
            issues.append(
                RepositoryReleaseCertificateVerificationIssue(
                    code="certificate_integrity_failure",
                    severity="critical",
                    message=(
                        "Certificate ID does not match the "
                        "certificate payload."
                    ),
                )
            )

        certified = (
            release_ready
            and certificate_status == "certified"
        )

        if release_ready and certificate_status != "certified":
            issues.append(
                RepositoryReleaseCertificateVerificationIssue(
                    code="inconsistent_ready_status",
                    severity="error",
                    message=(
                        "Release-ready certificate must have "
                        "status 'certified'."
                    ),
                )
            )

        if (
            not release_ready
            and certificate_status != "denied"
        ):
            issues.append(
                RepositoryReleaseCertificateVerificationIssue(
                    code="inconsistent_denied_status",
                    severity="error",
                    message=(
                        "Non-release-ready certificate must have "
                        "status 'denied'."
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
                RepositoryReleaseCertificateVerificationIssue(
                    code="certified_with_failed_evidence",
                    severity="critical",
                    message=(
                        "Certified release contains failed "
                        "evidence items."
                    ),
                )
            )

        if certified and denial_reasons:
            issues.append(
                RepositoryReleaseCertificateVerificationIssue(
                    code="certified_with_denial_reasons",
                    severity="error",
                    message=(
                        "Certified release contains denial reasons."
                    ),
                )
            )

        if (
            not certified
            and not denial_reasons
            and failed_evidence
        ):
            issues.append(
                RepositoryReleaseCertificateVerificationIssue(
                    code="denied_without_reasons",
                    severity="warning",
                    message=(
                        "Denied release contains failed evidence "
                        "but no denial reasons."
                    ),
                )
            )

        if require_certified and not certified:
            issues.append(
                RepositoryReleaseCertificateVerificationIssue(
                    code="certificate_not_certified",
                    severity="error",
                    message=(
                        "A certified release certificate is required."
                    ),
                )
            )

        if (
            expected_baseline_fingerprint is not None
            and baseline_fingerprint
            != expected_baseline_fingerprint
        ):
            issues.append(
                RepositoryReleaseCertificateVerificationIssue(
                    code="baseline_fingerprint_mismatch",
                    severity="critical",
                    message=(
                        "Certificate baseline fingerprint does not "
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
                RepositoryReleaseCertificateVerificationIssue(
                    code="candidate_fingerprint_mismatch",
                    severity="critical",
                    message=(
                        "Certificate candidate fingerprint does not "
                        "match the expected fingerprint."
                    ),
                )
            )

        return RepositoryReleaseCertificateVerification(
            certificate_id=certificate_id,
            repository_name=repository_name,
            schema_version=schema_version,
            certified=certified,
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
