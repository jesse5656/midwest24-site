from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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


ATTESTATION_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class RepositoryReleaseAttestationEvidence:
    name: str
    passed: bool
    severity: str
    message: str


@dataclass(frozen=True)
class RepositoryReleaseAttestation:
    schema_version: str
    repository_path: str
    repository_name: str
    attestation_id: str
    certificate_id: str
    certificate_valid: bool
    certified: bool
    baseline_fingerprint: str
    candidate_fingerprint: str
    evidence: list[RepositoryReleaseAttestationEvidence] = field(
        default_factory=list
    )
    issues: list[str] = field(default_factory=list)

    @property
    def evidence_count(self) -> int:
        return len(self.evidence)

    @property
    def passed_evidence_count(self) -> int:
        return sum(item.passed for item in self.evidence)

    @property
    def failed_evidence_count(self) -> int:
        return sum(not item.passed for item in self.evidence)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def accepted(self) -> bool:
        return (
            self.certificate_valid
            and self.certified
            and self.failed_evidence_count == 0
            and self.issue_count == 0
        )

    @property
    def rejected(self) -> bool:
        return not self.accepted

    @property
    def status(self) -> str:
        return (
            "attestation_accepted"
            if self.accepted
            else "attestation_rejected"
        )

    @property
    def evidence_names(self) -> list[str]:
        return [item.name for item in self.evidence]

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "repository_name": self.repository_name,
            "certificate_id": self.certificate_id,
            "certificate_valid": self.certificate_valid,
            "certified": self.certified,
            "baseline_fingerprint": self.baseline_fingerprint,
            "candidate_fingerprint": self.candidate_fingerprint,
            "evidence": [
                {
                    "name": item.name,
                    "passed": item.passed,
                    "severity": item.severity,
                    "message": item.message,
                }
                for item in sorted(
                    self.evidence,
                    key=lambda value: value.name,
                )
            ],
            "issues": sorted(self.issues),
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        )

    def as_json(self) -> str:
        payload = self.canonical_payload()
        payload["attestation_id"] = self.attestation_id

        return json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ) + "\n"


class RepositoryReleaseAttestationBuilder:
    def build(
        self,
        repository_path: str | Path,
        baseline: RepositorySnapshotBaseline,
        policy: RepositorySnapshotPolicy,
        max_depth: int = 8,
    ) -> RepositoryReleaseAttestation:
        certification = RepositoryReleaseCertificationBuilder().build(
            repository_path=repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=max_depth,
        )

        verification = RepositoryReleaseCertificateVerifier().verify_json(
            certification.as_json(),
            require_certified=False,
            expected_baseline_fingerprint=baseline.fingerprint,
            expected_candidate_fingerprint=(
                certification.candidate_fingerprint
            ),
        )

        return self.from_certification(
            certification=certification,
            verification=verification,
        )

    def from_certification(
        self,
        certification: RepositoryReleaseCertification,
        verification: RepositoryReleaseCertificateVerification,
    ) -> RepositoryReleaseAttestation:
        evidence = [
            RepositoryReleaseAttestationEvidence(
                name=item.name,
                passed=item.passed,
                severity=item.severity,
                message=item.message,
            )
            for item in certification.evidence
        ]

        issues = [
            issue.code
            for issue in verification.issues
        ]

        provisional = RepositoryReleaseAttestation(
            schema_version=ATTESTATION_SCHEMA_VERSION,
            repository_path=certification.repository_path,
            repository_name=certification.repository_name,
            attestation_id="",
            certificate_id=certification.certificate_id,
            certificate_valid=verification.valid,
            certified=certification.certified,
            baseline_fingerprint=(
                certification.baseline_fingerprint
            ),
            candidate_fingerprint=(
                certification.candidate_fingerprint
            ),
            evidence=evidence,
            issues=sorted(set(issues)),
        )

        attestation_id = hashlib.sha256(
            provisional.canonical_json().encode("utf-8")
        ).hexdigest()

        return RepositoryReleaseAttestation(
            schema_version=provisional.schema_version,
            repository_path=provisional.repository_path,
            repository_name=provisional.repository_name,
            attestation_id=attestation_id,
            certificate_id=provisional.certificate_id,
            certificate_valid=provisional.certificate_valid,
            certified=provisional.certified,
            baseline_fingerprint=provisional.baseline_fingerprint,
            candidate_fingerprint=provisional.candidate_fingerprint,
            evidence=provisional.evidence,
            issues=provisional.issues,
        )


def verify_release_attestation(
    attestation: RepositoryReleaseAttestation,
) -> bool:
    expected = hashlib.sha256(
        attestation.canonical_json().encode("utf-8")
    ).hexdigest()

    return expected == attestation.attestation_id
