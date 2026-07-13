from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.connectors.repository.repository_release_audit_bundle import (
    RELEASE_AUDIT_BUNDLE_SCHEMA_VERSION,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditBundleVerificationIssue:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class RepositoryReleaseAuditBundleVerification:
    bundle_id: str
    package_id: str
    report_id: str
    certificate_id: str
    attestation_id: str
    repository_name: str
    schema_version: str
    bundle_accepted: bool
    integrity_valid: bool
    issues: list[
        RepositoryReleaseAuditBundleVerificationIssue
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
        return self.valid and self.bundle_accepted

    @property
    def rejected(self) -> bool:
        return not self.accepted

    @property
    def status(self) -> str:
        if self.accepted:
            return "release_audit_bundle_accepted"

        if self.critical_issue_count > 0:
            return "release_audit_bundle_rejected_critical"

        if not self.valid:
            return "release_audit_bundle_rejected"

        return "release_audit_bundle_valid_not_accepted"


class RepositoryReleaseAuditBundleVerifier:
    required_fields = {
        "schema_version",
        "repository_name",
        "bundle_id",
        "accepted",
        "status",
        "exit_code",
        "package_id",
        "package_accepted",
        "report_id",
        "report_accepted",
        "certificate_id",
        "attestation_id",
        "baseline_fingerprint",
        "candidate_fingerprint",
    }

    def verify_json(
        self,
        bundle_json: str,
        require_accepted: bool = True,
        expected_package_id: str | None = None,
        expected_report_id: str | None = None,
        expected_certificate_id: str | None = None,
        expected_attestation_id: str | None = None,
        expected_baseline_fingerprint: str | None = None,
        expected_candidate_fingerprint: str | None = None,
    ) -> RepositoryReleaseAuditBundleVerification:
        try:
            payload = json.loads(bundle_json)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid release audit bundle JSON: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "Release audit bundle JSON must contain an object."
            )

        missing = sorted(
            self.required_fields - set(payload)
        )

        if missing:
            raise ValueError(
                "Release audit bundle is missing required field(s): "
                + ", ".join(missing)
            )

        return self.verify_payload(
            payload=payload,
            require_accepted=require_accepted,
            expected_package_id=expected_package_id,
            expected_report_id=expected_report_id,
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
        expected_package_id: str | None = None,
        expected_report_id: str | None = None,
        expected_certificate_id: str | None = None,
        expected_attestation_id: str | None = None,
        expected_baseline_fingerprint: str | None = None,
        expected_candidate_fingerprint: str | None = None,
    ) -> RepositoryReleaseAuditBundleVerification:
        issues: list[
            RepositoryReleaseAuditBundleVerificationIssue
        ] = []

        schema_version = str(
            payload.get("schema_version", "")
        )
        repository_name = str(
            payload.get("repository_name", "")
        )
        bundle_id = str(
            payload.get("bundle_id", "")
        )
        bundle_accepted = bool(
            payload.get("accepted", False)
        )
        bundle_status = str(
            payload.get("status", "")
        )
        exit_code = int(
            payload.get("exit_code", 1)
        )
        package_id = str(
            payload.get("package_id", "")
        )
        package_accepted = bool(
            payload.get("package_accepted", False)
        )
        report_id = str(
            payload.get("report_id", "")
        )
        report_accepted = bool(
            payload.get("report_accepted", False)
        )
        certificate_id = str(
            payload.get("certificate_id", "")
        )
        attestation_id = str(
            payload.get("attestation_id", "")
        )
        baseline_fingerprint = str(
            payload.get("baseline_fingerprint", "")
        )
        candidate_fingerprint = str(
            payload.get("candidate_fingerprint", "")
        )

        if schema_version != RELEASE_AUDIT_BUNDLE_SCHEMA_VERSION:
            issues.append(
                RepositoryReleaseAuditBundleVerificationIssue(
                    code="unsupported_schema_version",
                    severity="critical",
                    message=(
                        f"Audit bundle schema version "
                        f"{schema_version!r} is not supported."
                    ),
                )
            )

        if not repository_name.strip():
            issues.append(
                RepositoryReleaseAuditBundleVerificationIssue(
                    code="missing_repository_name",
                    severity="error",
                    message="Audit bundle repository name is empty.",
                )
            )

        digest_values = {
            "bundle_id": bundle_id,
            "package_id": package_id,
            "report_id": report_id,
            "certificate_id": certificate_id,
            "attestation_id": attestation_id,
            "baseline_fingerprint": baseline_fingerprint,
            "candidate_fingerprint": candidate_fingerprint,
        }

        for name, value in digest_values.items():
            if not self._is_sha256(value):
                issues.append(
                    RepositoryReleaseAuditBundleVerificationIssue(
                        code=f"invalid_{name}",
                        severity="critical",
                        message=(
                            f"{name} is not a valid SHA-256 digest."
                        ),
                    )
                )

        canonical_payload = {
            "schema_version": schema_version,
            "repository_name": repository_name,
            "package_id": package_id,
            "package_accepted": package_accepted,
            "report_id": report_id,
            "report_accepted": report_accepted,
            "certificate_id": certificate_id,
            "attestation_id": attestation_id,
            "baseline_fingerprint": baseline_fingerprint,
            "candidate_fingerprint": candidate_fingerprint,
        }

        expected_bundle_id = hashlib.sha256(
            json.dumps(
                canonical_payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        integrity_valid = bundle_id == expected_bundle_id

        if not integrity_valid:
            issues.append(
                RepositoryReleaseAuditBundleVerificationIssue(
                    code="bundle_integrity_failure",
                    severity="critical",
                    message=(
                        "Bundle ID does not match the bundle payload."
                    ),
                )
            )

        expected_status = (
            "release_audit_bundle_accepted"
            if bundle_accepted
            else "release_audit_bundle_rejected"
        )

        if bundle_status != expected_status:
            issues.append(
                RepositoryReleaseAuditBundleVerificationIssue(
                    code="inconsistent_bundle_status",
                    severity="error",
                    message=(
                        f"Bundle status {bundle_status!r} does not "
                        f"match accepted state {bundle_accepted}."
                    ),
                )
            )

        expected_exit_code = 0 if bundle_accepted else 1

        if exit_code != expected_exit_code:
            issues.append(
                RepositoryReleaseAuditBundleVerificationIssue(
                    code="inconsistent_exit_code",
                    severity="error",
                    message=(
                        f"Bundle exit code {exit_code} does not match "
                        f"accepted state {bundle_accepted}."
                    ),
                )
            )

        if bundle_accepted and not package_accepted:
            issues.append(
                RepositoryReleaseAuditBundleVerificationIssue(
                    code="accepted_with_rejected_package",
                    severity="critical",
                    message=(
                        "Accepted audit bundle contains a rejected "
                        "evidence package."
                    ),
                )
            )

        if bundle_accepted and not report_accepted:
            issues.append(
                RepositoryReleaseAuditBundleVerificationIssue(
                    code="accepted_with_rejected_report",
                    severity="critical",
                    message=(
                        "Accepted audit bundle contains a rejected "
                        "audit report."
                    ),
                )
            )

        if require_accepted and not bundle_accepted:
            issues.append(
                RepositoryReleaseAuditBundleVerificationIssue(
                    code="bundle_not_accepted",
                    severity="error",
                    message=(
                        "An accepted release audit bundle is required."
                    ),
                )
            )

        expectations = {
            "package_id_mismatch": (
                expected_package_id,
                package_id,
                "package ID",
            ),
            "report_id_mismatch": (
                expected_report_id,
                report_id,
                "report ID",
            ),
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
                    RepositoryReleaseAuditBundleVerificationIssue(
                        code=code,
                        severity="critical",
                        message=(
                            f"Audit bundle {label} does not match "
                            f"the expected value."
                        ),
                    )
                )

        return RepositoryReleaseAuditBundleVerification(
            bundle_id=bundle_id,
            package_id=package_id,
            report_id=report_id,
            certificate_id=certificate_id,
            attestation_id=attestation_id,
            repository_name=repository_name,
            schema_version=schema_version,
            bundle_accepted=bundle_accepted,
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
