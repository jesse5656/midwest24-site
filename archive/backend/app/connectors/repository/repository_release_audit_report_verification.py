from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.connectors.repository.repository_release_audit_report import (
    RELEASE_AUDIT_REPORT_SCHEMA_VERSION,
)


@dataclass(frozen=True)
class RepositoryReleaseAuditReportVerificationIssue:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class RepositoryReleaseAuditReportVerification:
    report_id: str
    package_id: str
    certificate_id: str
    attestation_id: str
    repository_name: str
    schema_version: str
    report_passed: bool
    integrity_valid: bool
    issues: list[
        RepositoryReleaseAuditReportVerificationIssue
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
        return self.valid and self.report_passed

    @property
    def rejected(self) -> bool:
        return not self.accepted

    @property
    def status(self) -> str:
        if self.accepted:
            return "release_audit_report_accepted"

        if self.critical_issue_count > 0:
            return "release_audit_report_rejected_critical"

        if not self.valid:
            return "release_audit_report_rejected"

        return "release_audit_report_valid_not_passed"


class RepositoryReleaseAuditReportVerifier:
    required_fields = {
        "schema_version",
        "report_id",
        "package_id",
        "repository_name",
        "accepted",
        "integrity_valid",
        "passed",
        "exit_code",
        "status",
        "certificate_id",
        "attestation_id",
        "findings",
    }

    def verify_json(
        self,
        report_json: str,
        require_passed: bool = True,
        expected_package_id: str | None = None,
        expected_certificate_id: str | None = None,
        expected_attestation_id: str | None = None,
    ) -> RepositoryReleaseAuditReportVerification:
        try:
            payload = json.loads(report_json)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid release audit report JSON: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "Release audit report JSON must contain an object."
            )

        missing = sorted(
            self.required_fields - set(payload)
        )

        if missing:
            raise ValueError(
                "Release audit report is missing required field(s): "
                + ", ".join(missing)
            )

        return self.verify_payload(
            payload=payload,
            require_passed=require_passed,
            expected_package_id=expected_package_id,
            expected_certificate_id=expected_certificate_id,
            expected_attestation_id=expected_attestation_id,
        )

    def verify_payload(
        self,
        payload: dict[str, Any],
        require_passed: bool = True,
        expected_package_id: str | None = None,
        expected_certificate_id: str | None = None,
        expected_attestation_id: str | None = None,
    ) -> RepositoryReleaseAuditReportVerification:
        issues: list[
            RepositoryReleaseAuditReportVerificationIssue
        ] = []

        schema_version = str(
            payload.get("schema_version", "")
        )
        report_id = str(payload.get("report_id", ""))
        package_id = str(payload.get("package_id", ""))
        repository_name = str(
            payload.get("repository_name", "")
        )
        accepted = bool(payload.get("accepted", False))
        integrity_valid_value = bool(
            payload.get("integrity_valid", False)
        )
        report_passed = bool(payload.get("passed", False))
        exit_code = int(payload.get("exit_code", 1))
        report_status = str(payload.get("status", ""))
        certificate_id = str(
            payload.get("certificate_id", "")
        )
        attestation_id = str(
            payload.get("attestation_id", "")
        )
        findings = payload.get("findings", [])

        if schema_version != RELEASE_AUDIT_REPORT_SCHEMA_VERSION:
            issues.append(
                RepositoryReleaseAuditReportVerificationIssue(
                    code="unsupported_schema_version",
                    severity="critical",
                    message=(
                        f"Audit report schema version "
                        f"{schema_version!r} is not supported."
                    ),
                )
            )

        if not repository_name.strip():
            issues.append(
                RepositoryReleaseAuditReportVerificationIssue(
                    code="missing_repository_name",
                    severity="error",
                    message="Audit report repository name is empty.",
                )
            )

        for name, value in {
            "report_id": report_id,
            "package_id": package_id,
            "certificate_id": certificate_id,
            "attestation_id": attestation_id,
        }.items():
            if not self._is_sha256(value):
                issues.append(
                    RepositoryReleaseAuditReportVerificationIssue(
                        code=f"invalid_{name}",
                        severity="critical",
                        message=(
                            f"{name} is not a valid SHA-256 digest."
                        ),
                    )
                )

        normalized_findings = self._normalize_findings(
            findings
        )

        canonical_payload = {
            "schema_version": schema_version,
            "package_id": package_id,
            "repository_name": repository_name,
            "accepted": accepted,
            "integrity_valid": integrity_valid_value,
            "status": report_status,
            "certificate_id": certificate_id,
            "attestation_id": attestation_id,
            "findings": normalized_findings,
        }

        expected_report_id = hashlib.sha256(
            json.dumps(
                canonical_payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        integrity_valid = report_id == expected_report_id

        if not integrity_valid:
            issues.append(
                RepositoryReleaseAuditReportVerificationIssue(
                    code="report_integrity_failure",
                    severity="critical",
                    message=(
                        "Report ID does not match the report payload."
                    ),
                )
            )

        if integrity_valid_value != integrity_valid:
            issues.append(
                RepositoryReleaseAuditReportVerificationIssue(
                    code="inconsistent_integrity_state",
                    severity="error",
                    message=(
                        "Stored integrity state does not match "
                        "calculated report integrity."
                    ),
                )
            )

        expected_status = (
            "audit_passed"
            if report_passed
            else "audit_failed"
        )

        if report_status != expected_status:
            issues.append(
                RepositoryReleaseAuditReportVerificationIssue(
                    code="inconsistent_report_status",
                    severity="error",
                    message=(
                        f"Report status {report_status!r} does not "
                        f"match passed state {report_passed}."
                    ),
                )
            )

        expected_exit_code = 0 if report_passed else 1

        if exit_code != expected_exit_code:
            issues.append(
                RepositoryReleaseAuditReportVerificationIssue(
                    code="inconsistent_exit_code",
                    severity="error",
                    message=(
                        f"Report exit code {exit_code} does not match "
                        f"passed state {report_passed}."
                    ),
                )
            )

        critical_findings = [
            finding
            for finding in normalized_findings
            if finding["severity"] == "critical"
        ]

        error_findings = [
            finding
            for finding in normalized_findings
            if finding["severity"] == "error"
        ]

        if report_passed and critical_findings:
            issues.append(
                RepositoryReleaseAuditReportVerificationIssue(
                    code="passed_with_critical_findings",
                    severity="critical",
                    message=(
                        "Passed audit report contains critical findings."
                    ),
                )
            )

        if report_passed and error_findings:
            issues.append(
                RepositoryReleaseAuditReportVerificationIssue(
                    code="passed_with_error_findings",
                    severity="error",
                    message=(
                        "Passed audit report contains error findings."
                    ),
                )
            )

        if report_passed and not accepted:
            issues.append(
                RepositoryReleaseAuditReportVerificationIssue(
                    code="passed_without_package_acceptance",
                    severity="critical",
                    message=(
                        "Passed audit report does not indicate "
                        "package acceptance."
                    ),
                )
            )

        if require_passed and not report_passed:
            issues.append(
                RepositoryReleaseAuditReportVerificationIssue(
                    code="audit_report_not_passed",
                    severity="error",
                    message=(
                        "A passing release audit report is required."
                    ),
                )
            )

        expectations = {
            "package_id_mismatch": (
                expected_package_id,
                package_id,
                "package ID",
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
        }

        for code, values in expectations.items():
            expected, actual, label = values

            if expected is not None and actual != expected:
                issues.append(
                    RepositoryReleaseAuditReportVerificationIssue(
                        code=code,
                        severity="critical",
                        message=(
                            f"Audit report {label} does not match "
                            f"the expected value."
                        ),
                    )
                )

        return RepositoryReleaseAuditReportVerification(
            report_id=report_id,
            package_id=package_id,
            certificate_id=certificate_id,
            attestation_id=attestation_id,
            repository_name=repository_name,
            schema_version=schema_version,
            report_passed=report_passed,
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

    def _normalize_findings(
        self,
        findings: Any,
    ) -> list[dict[str, str]]:
        if not isinstance(findings, list):
            return []

        normalized = []

        for finding in findings:
            if not isinstance(finding, dict):
                continue

            normalized.append(
                {
                    "code": str(finding.get("code", "")),
                    "severity": str(
                        finding.get("severity", "")
                    ),
                    "message": str(
                        finding.get("message", "")
                    ),
                }
            )

        return sorted(
            normalized,
            key=lambda finding: (
                finding["severity"],
                finding["code"],
                finding["message"],
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
