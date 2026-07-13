from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.connectors.repository.repository_release_readiness import (
    RepositoryReleaseReadiness,
    RepositoryReleaseReadinessEvaluator,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)


CERTIFICATION_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class RepositoryReleaseCertificationEvidence:
    name: str
    passed: bool
    severity: str
    message: str


@dataclass(frozen=True)
class RepositoryReleaseCertification:
    schema_version: str
    repository_path: str
    repository_name: str
    release_ready: bool
    status: str
    certificate_id: str
    baseline_fingerprint: str
    candidate_fingerprint: str
    evidence: list[RepositoryReleaseCertificationEvidence] = field(
        default_factory=list
    )
    denial_reasons: list[str] = field(default_factory=list)

    @property
    def certified(self) -> bool:
        return self.release_ready and self.status == "certified"

    @property
    def denied(self) -> bool:
        return not self.certified

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
    def critical_failure_count(self) -> int:
        return sum(
            not item.passed and item.severity == "critical"
            for item in self.evidence
        )

    @property
    def denial_reason_count(self) -> int:
        return len(self.denial_reasons)

    @property
    def evidence_names(self) -> list[str]:
        return [item.name for item in self.evidence]

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "repository_name": self.repository_name,
            "release_ready": self.release_ready,
            "status": self.status,
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
            "denial_reasons": sorted(self.denial_reasons),
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        )

    def as_json(self) -> str:
        payload = self.canonical_payload()
        payload["certificate_id"] = self.certificate_id

        return json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ) + "\n"


class RepositoryReleaseCertificationBuilder:
    def build(
        self,
        repository_path: str | Path,
        baseline: RepositorySnapshotBaseline,
        policy: RepositorySnapshotPolicy,
        max_depth: int = 8,
    ) -> RepositoryReleaseCertification:
        readiness = RepositoryReleaseReadinessEvaluator().evaluate(
            repository_path=repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=max_depth,
        )

        return self.from_readiness(
            readiness=readiness,
            baseline=baseline,
        )

    def from_readiness(
        self,
        readiness: RepositoryReleaseReadiness,
        baseline: RepositorySnapshotBaseline,
    ) -> RepositoryReleaseCertification:
        evidence = [
            RepositoryReleaseCertificationEvidence(
                name=check.name,
                passed=check.passed,
                severity=check.severity,
                message=check.message,
            )
            for check in readiness.checks
        ]

        denial_reasons = [
            check.name
            for check in readiness.checks
            if not check.passed
        ]

        status = (
            "certified"
            if readiness.release_ready
            else "denied"
        )

        provisional = RepositoryReleaseCertification(
            schema_version=CERTIFICATION_SCHEMA_VERSION,
            repository_path=readiness.repository_path,
            repository_name=readiness.repository_name,
            release_ready=readiness.release_ready,
            status=status,
            certificate_id="",
            baseline_fingerprint=baseline.fingerprint,
            candidate_fingerprint=(
                readiness.gate
                .baseline_verification
                .candidate
                .fingerprint
            ),
            evidence=evidence,
            denial_reasons=denial_reasons,
        )

        certificate_id = hashlib.sha256(
            provisional.canonical_json().encode("utf-8")
        ).hexdigest()

        return RepositoryReleaseCertification(
            schema_version=provisional.schema_version,
            repository_path=provisional.repository_path,
            repository_name=provisional.repository_name,
            release_ready=provisional.release_ready,
            status=provisional.status,
            certificate_id=certificate_id,
            baseline_fingerprint=provisional.baseline_fingerprint,
            candidate_fingerprint=provisional.candidate_fingerprint,
            evidence=provisional.evidence,
            denial_reasons=provisional.denial_reasons,
        )


def verify_release_certificate(
    certification: RepositoryReleaseCertification,
) -> bool:
    expected = hashlib.sha256(
        certification.canonical_json().encode("utf-8")
    ).hexdigest()

    return expected == certification.certificate_id
