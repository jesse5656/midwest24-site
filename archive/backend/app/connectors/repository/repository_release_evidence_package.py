from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.connectors.repository.repository_release_attestation import (
    RepositoryReleaseAttestation,
    RepositoryReleaseAttestationBuilder,
)
from app.connectors.repository.repository_release_attestation_verification import (
    RepositoryReleaseAttestationVerification,
    RepositoryReleaseAttestationVerifier,
)
from app.connectors.repository.repository_release_certificate_verification import (
    RepositoryReleaseCertificateVerification,
    RepositoryReleaseCertificateVerifier,
)
from app.connectors.repository.repository_release_certification import (
    RepositoryReleaseCertification,
    RepositoryReleaseCertificationBuilder,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)


RELEASE_EVIDENCE_PACKAGE_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class RepositoryReleaseEvidenceItem:
    name: str
    status: str
    reference: str


@dataclass(frozen=True)
class RepositoryReleaseEvidencePackage:
    schema_version: str
    repository_path: str
    repository_name: str
    package_id: str
    certificate: RepositoryReleaseCertification
    certificate_verification: (
        RepositoryReleaseCertificateVerification
    )
    attestation: RepositoryReleaseAttestation
    attestation_verification: (
        RepositoryReleaseAttestationVerification
    )
    evidence: list[RepositoryReleaseEvidenceItem] = field(
        default_factory=list
    )

    @property
    def evidence_count(self) -> int:
        return len(self.evidence)

    @property
    def accepted(self) -> bool:
        return (
            self.certificate.certified
            and self.certificate_verification.accepted
            and self.attestation.accepted
            and self.attestation_verification.accepted
        )

    @property
    def rejected(self) -> bool:
        return not self.accepted

    @property
    def status(self) -> str:
        return (
            "release_package_accepted"
            if self.accepted
            else "release_package_rejected"
        )

    @property
    def failed_component_count(self) -> int:
        states = [
            self.certificate.certified,
            self.certificate_verification.accepted,
            self.attestation.accepted,
            self.attestation_verification.accepted,
        ]
        return sum(not state for state in states)

    @property
    def component_names(self) -> list[str]:
        return [
            "certificate",
            "certificate_verification",
            "attestation",
            "attestation_verification",
        ]

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "repository_name": self.repository_name,
            "certificate_id": self.certificate.certificate_id,
            "certificate_accepted": (
                self.certificate_verification.accepted
            ),
            "attestation_id": self.attestation.attestation_id,
            "attestation_accepted": (
                self.attestation_verification.accepted
            ),
            "baseline_fingerprint": (
                self.certificate.baseline_fingerprint
            ),
            "candidate_fingerprint": (
                self.certificate.candidate_fingerprint
            ),
            "evidence": [
                {
                    "name": item.name,
                    "status": item.status,
                    "reference": item.reference,
                }
                for item in sorted(
                    self.evidence,
                    key=lambda value: value.name,
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
        payload["package_id"] = self.package_id
        payload["accepted"] = self.accepted
        payload["status"] = self.status

        return json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ) + "\n"


class RepositoryReleaseEvidencePackageBuilder:
    def build(
        self,
        repository_path: str | Path,
        baseline: RepositorySnapshotBaseline,
        policy: RepositorySnapshotPolicy,
        max_depth: int = 8,
    ) -> RepositoryReleaseEvidencePackage:
        certification = RepositoryReleaseCertificationBuilder().build(
            repository_path=repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=max_depth,
        )

        certificate_verification = (
            RepositoryReleaseCertificateVerifier()
            .verify_json(
                certificate_json=certification.as_json(),
                require_certified=False,
                expected_baseline_fingerprint=(
                    baseline.fingerprint
                ),
                expected_candidate_fingerprint=(
                    certification.candidate_fingerprint
                ),
            )
        )

        attestation = RepositoryReleaseAttestationBuilder().build(
            repository_path=repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=max_depth,
        )

        attestation_verification = (
            RepositoryReleaseAttestationVerifier()
            .verify_json(
                attestation_json=attestation.as_json(),
                require_accepted=False,
                expected_certificate_id=(
                    attestation.certificate_id
                ),
                expected_baseline_fingerprint=(
                    baseline.fingerprint
                ),
                expected_candidate_fingerprint=(
                    attestation.candidate_fingerprint
                ),
            )
        )

        return self.from_components(
            repository_path=str(repository_path),
            certification=certification,
            certificate_verification=certificate_verification,
            attestation=attestation,
            attestation_verification=(
                attestation_verification
            ),
        )

    def from_components(
        self,
        repository_path: str,
        certification: RepositoryReleaseCertification,
        certificate_verification: (
            RepositoryReleaseCertificateVerification
        ),
        attestation: RepositoryReleaseAttestation,
        attestation_verification: (
            RepositoryReleaseAttestationVerification
        ),
    ) -> RepositoryReleaseEvidencePackage:
        evidence = [
            RepositoryReleaseEvidenceItem(
                name="release_certificate",
                status=(
                    "accepted"
                    if certificate_verification.accepted
                    else "rejected"
                ),
                reference=certification.certificate_id,
            ),
            RepositoryReleaseEvidenceItem(
                name="release_attestation",
                status=(
                    "accepted"
                    if attestation_verification.accepted
                    else "rejected"
                ),
                reference=attestation.attestation_id,
            ),
            RepositoryReleaseEvidenceItem(
                name="baseline_fingerprint",
                status="recorded",
                reference=certification.baseline_fingerprint,
            ),
            RepositoryReleaseEvidenceItem(
                name="candidate_fingerprint",
                status="recorded",
                reference=certification.candidate_fingerprint,
            ),
        ]

        provisional = RepositoryReleaseEvidencePackage(
            schema_version=(
                RELEASE_EVIDENCE_PACKAGE_SCHEMA_VERSION
            ),
            repository_path=repository_path,
            repository_name=certification.repository_name,
            package_id="",
            certificate=certification,
            certificate_verification=certificate_verification,
            attestation=attestation,
            attestation_verification=attestation_verification,
            evidence=evidence,
        )

        package_id = hashlib.sha256(
            provisional.canonical_json().encode("utf-8")
        ).hexdigest()

        return RepositoryReleaseEvidencePackage(
            schema_version=provisional.schema_version,
            repository_path=provisional.repository_path,
            repository_name=provisional.repository_name,
            package_id=package_id,
            certificate=provisional.certificate,
            certificate_verification=(
                provisional.certificate_verification
            ),
            attestation=provisional.attestation,
            attestation_verification=(
                provisional.attestation_verification
            ),
            evidence=provisional.evidence,
        )


def verify_release_evidence_package(
    package: RepositoryReleaseEvidencePackage,
) -> bool:
    expected = hashlib.sha256(
        package.canonical_json().encode("utf-8")
    ).hexdigest()

    return expected == package.package_id
