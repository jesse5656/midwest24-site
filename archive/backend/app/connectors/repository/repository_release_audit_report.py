from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.connectors.repository.repository_release_evidence_package_verification import (
    RepositoryReleaseEvidencePackageVerification,
    RepositoryReleaseEvidencePackageVerifier,
)


RELEASE_AUDIT_REPORT_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class RepositoryReleaseAuditFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class RepositoryReleaseAuditReport:
    schema_version: str
    report_id: str
    package_id: str
    repository_name: str
    accepted: bool
    integrity_valid: bool
    status: str
    certificate_id: str
    attestation_id: str
    findings: list[RepositoryReleaseAuditFinding] = field(
        default_factory=list
    )

    @property
    def finding_count(self) -> int:
        return len(self.findings)

    @property
    def critical_finding_count(self) -> int:
        return sum(
            finding.severity == "critical"
            for finding in self.findings
        )

    @property
    def error_finding_count(self) -> int:
        return sum(
            finding.severity == "error"
            for finding in self.findings
        )

    @property
    def warning_finding_count(self) -> int:
        return sum(
            finding.severity == "warning"
            for finding in self.findings
        )

    @property
    def finding_codes(self) -> list[str]:
        return sorted(
            {
                finding.code
                for finding in self.findings
            }
        )

    @property
    def passed(self) -> bool:
        return (
            self.accepted
            and self.integrity_valid
            and self.critical_finding_count == 0
            and self.error_finding_count == 0
        )

    @property
    def failed(self) -> bool:
        return not self.passed

    @property
    def exit_code(self) -> int:
        return 0 if self.passed else 1

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "package_id": self.package_id,
            "repository_name": self.repository_name,
            "accepted": self.accepted,
            "integrity_valid": self.integrity_valid,
            "status": self.status,
            "certificate_id": self.certificate_id,
            "attestation_id": self.attestation_id,
            "findings": [
                {
                    "code": finding.code,
                    "severity": finding.severity,
                    "message": finding.message,
                }
                for finding in sorted(
                    self.findings,
                    key=lambda item: (
                        item.severity,
                        item.code,
                        item.message,
                    ),
                )
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
        payload["report_id"] = self.report_id
        payload["passed"] = self.passed
        payload["exit_code"] = self.exit_code

        return json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ) + "\n"

    def as_markdown(self) -> str:
        lines = [
            "# Repository Release Audit Report",
            "",
            f"- **Repository:** {self.repository_name}",
            f"- **Report ID:** `{self.report_id}`",
            f"- **Package ID:** `{self.package_id}`",
            f"- **Certificate ID:** `{self.certificate_id}`",
            f"- **Attestation ID:** `{self.attestation_id}`",
            f"- **Status:** {self.status}",
            f"- **Passed:** {'Yes' if self.passed else 'No'}",
            f"- **Integrity valid:** "
            f"{'Yes' if self.integrity_valid else 'No'}",
            "",
            "## Findings",
            "",
        ]

        if not self.findings:
            lines.append("- No audit findings.")

        for finding in self.findings:
            lines.append(
                f"- **{finding.severity.upper()} — "
                f"{finding.code}:** {finding.message}"
            )

        return "\n".join(lines).rstrip() + "\n"


class RepositoryReleaseAuditReportBuilder:
    def build(
        self,
        package_json: str,
        require_accepted: bool = True,
        expected_certificate_id: str | None = None,
        expected_attestation_id: str | None = None,
        expected_baseline_fingerprint: str | None = None,
        expected_candidate_fingerprint: str | None = None,
    ) -> RepositoryReleaseAuditReport:
        verification = (
            RepositoryReleaseEvidencePackageVerifier()
            .verify_json(
                package_json=package_json,
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
        )

        return self.from_verification(verification)

    def from_verification(
        self,
        verification: RepositoryReleaseEvidencePackageVerification,
    ) -> RepositoryReleaseAuditReport:
        findings = [
            RepositoryReleaseAuditFinding(
                code=issue.code,
                severity=issue.severity,
                message=issue.message,
            )
            for issue in verification.issues
        ]

        status = (
            "audit_passed"
            if verification.accepted
            else "audit_failed"
        )

        provisional = RepositoryReleaseAuditReport(
            schema_version=RELEASE_AUDIT_REPORT_SCHEMA_VERSION,
            report_id="",
            package_id=verification.package_id,
            repository_name=verification.repository_name,
            accepted=verification.accepted,
            integrity_valid=verification.integrity_valid,
            status=status,
            certificate_id=verification.certificate_id,
            attestation_id=verification.attestation_id,
            findings=findings,
        )

        report_id = hashlib.sha256(
            provisional.canonical_json().encode("utf-8")
        ).hexdigest()

        return RepositoryReleaseAuditReport(
            schema_version=provisional.schema_version,
            report_id=report_id,
            package_id=provisional.package_id,
            repository_name=provisional.repository_name,
            accepted=provisional.accepted,
            integrity_valid=provisional.integrity_valid,
            status=provisional.status,
            certificate_id=provisional.certificate_id,
            attestation_id=provisional.attestation_id,
            findings=provisional.findings,
        )


def verify_release_audit_report(
    report: RepositoryReleaseAuditReport,
) -> bool:
    expected = hashlib.sha256(
        report.canonical_json().encode("utf-8")
    ).hexdigest()

    return expected == report.report_id
