from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.connectors.repository.repository_release_audit_report import (
    RepositoryReleaseAuditReport,
    RepositoryReleaseAuditReportBuilder,
)
from app.connectors.repository.repository_release_audit_report_verification import (
    RepositoryReleaseAuditReportVerification,
    RepositoryReleaseAuditReportVerifier,
)
from app.connectors.repository.repository_release_evidence_package import (
    RepositoryReleaseEvidencePackage,
    RepositoryReleaseEvidencePackageBuilder,
)
from app.connectors.repository.repository_release_evidence_package_verification import (
    RepositoryReleaseEvidencePackageVerification,
    RepositoryReleaseEvidencePackageVerifier,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)


RELEASE_AUDIT_BUNDLE_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class RepositoryReleaseAuditBundle:
    schema_version: str
    repository_path: str
    repository_name: str
    bundle_id: str
    package: RepositoryReleaseEvidencePackage
    package_verification: RepositoryReleaseEvidencePackageVerification
    audit_report: RepositoryReleaseAuditReport
    audit_verification: RepositoryReleaseAuditReportVerification

    @property
    def package_id(self) -> str:
        return self.package.package_id

    @property
    def report_id(self) -> str:
        return self.audit_report.report_id

    @property
    def certificate_id(self) -> str:
        return self.package.certificate.certificate_id

    @property
    def attestation_id(self) -> str:
        return self.package.attestation.attestation_id

    @property
    def accepted(self) -> bool:
        return (
            self.package.accepted
            and self.package_verification.accepted
            and self.audit_report.passed
            and self.audit_verification.accepted
        )

    @property
    def rejected(self) -> bool:
        return not self.accepted

    @property
    def status(self) -> str:
        return (
            "release_audit_bundle_accepted"
            if self.accepted
            else "release_audit_bundle_rejected"
        )

    @property
    def failed_component_count(self) -> int:
        states = [
            self.package.accepted,
            self.package_verification.accepted,
            self.audit_report.passed,
            self.audit_verification.accepted,
        ]

        return sum(not state for state in states)

    @property
    def component_names(self) -> list[str]:
        return [
            "evidence_package",
            "evidence_package_verification",
            "audit_report",
            "audit_report_verification",
        ]

    @property
    def exit_code(self) -> int:
        return 0 if self.accepted else 1

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "repository_name": self.repository_name,
            "package_id": self.package_id,
            "package_accepted": self.package_verification.accepted,
            "report_id": self.report_id,
            "report_accepted": self.audit_verification.accepted,
            "certificate_id": self.certificate_id,
            "attestation_id": self.attestation_id,
            "baseline_fingerprint": (
                self.package.certificate.baseline_fingerprint
            ),
            "candidate_fingerprint": (
                self.package.certificate.candidate_fingerprint
            ),
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        )

    def as_json(self) -> str:
        payload = self.canonical_payload()
        payload["bundle_id"] = self.bundle_id
        payload["accepted"] = self.accepted
        payload["status"] = self.status
        payload["exit_code"] = self.exit_code

        return json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ) + "\n"

    def as_markdown(self) -> str:
        return "\n".join(
            [
                "# Repository Release Audit Bundle",
                "",
                f"- **Repository:** {self.repository_name}",
                f"- **Bundle ID:** `{self.bundle_id}`",
                f"- **Package ID:** `{self.package_id}`",
                f"- **Audit Report ID:** `{self.report_id}`",
                f"- **Certificate ID:** `{self.certificate_id}`",
                f"- **Attestation ID:** `{self.attestation_id}`",
                f"- **Status:** {self.status}",
                f"- **Accepted:** {'Yes' if self.accepted else 'No'}",
                f"- **Exit code:** {self.exit_code}",
                "",
            ]
        )


class RepositoryReleaseAuditBundleBuilder:
    def build(
        self,
        repository_path: str,
        baseline: RepositorySnapshotBaseline,
        policy: RepositorySnapshotPolicy,
        max_depth: int = 8,
    ) -> RepositoryReleaseAuditBundle:
        package = RepositoryReleaseEvidencePackageBuilder().build(
            repository_path=repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=max_depth,
        )

        package_verification = (
            RepositoryReleaseEvidencePackageVerifier()
            .verify_json(
                package_json=package.as_json(),
                require_accepted=False,
                expected_certificate_id=(
                    package.certificate.certificate_id
                ),
                expected_attestation_id=(
                    package.attestation.attestation_id
                ),
                expected_baseline_fingerprint=(
                    package.certificate.baseline_fingerprint
                ),
                expected_candidate_fingerprint=(
                    package.certificate.candidate_fingerprint
                ),
            )
        )

        audit_report = RepositoryReleaseAuditReportBuilder().build(
            package_json=package.as_json(),
            require_accepted=False,
        )

        audit_verification = (
            RepositoryReleaseAuditReportVerifier()
            .verify_json(
                report_json=audit_report.as_json(),
                require_passed=False,
                expected_package_id=package.package_id,
                expected_certificate_id=(
                    package.certificate.certificate_id
                ),
                expected_attestation_id=(
                    package.attestation.attestation_id
                ),
            )
        )

        return self.from_components(
            repository_path=repository_path,
            package=package,
            package_verification=package_verification,
            audit_report=audit_report,
            audit_verification=audit_verification,
        )

    def from_components(
        self,
        repository_path: str,
        package: RepositoryReleaseEvidencePackage,
        package_verification: RepositoryReleaseEvidencePackageVerification,
        audit_report: RepositoryReleaseAuditReport,
        audit_verification: RepositoryReleaseAuditReportVerification,
    ) -> RepositoryReleaseAuditBundle:
        provisional = RepositoryReleaseAuditBundle(
            schema_version=RELEASE_AUDIT_BUNDLE_SCHEMA_VERSION,
            repository_path=repository_path,
            repository_name=package.repository_name,
            bundle_id="",
            package=package,
            package_verification=package_verification,
            audit_report=audit_report,
            audit_verification=audit_verification,
        )

        bundle_id = hashlib.sha256(
            provisional.canonical_json().encode("utf-8")
        ).hexdigest()

        return RepositoryReleaseAuditBundle(
            schema_version=provisional.schema_version,
            repository_path=provisional.repository_path,
            repository_name=provisional.repository_name,
            bundle_id=bundle_id,
            package=provisional.package,
            package_verification=provisional.package_verification,
            audit_report=provisional.audit_report,
            audit_verification=provisional.audit_verification,
        )


def verify_release_audit_bundle(
    bundle: RepositoryReleaseAuditBundle,
) -> bool:
    expected = hashlib.sha256(
        bundle.canonical_json().encode("utf-8")
    ).hexdigest()

    return expected == bundle.bundle_id
