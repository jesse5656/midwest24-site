from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_attestation import (
    RepositoryReleaseAttestation,
    RepositoryReleaseAttestationBuilder,
    RepositoryReleaseAttestationEvidence,
    verify_release_attestation,
)
from app.connectors.repository.repository_release_attestation_summary import (
    RepositoryReleaseAttestationSummaryBuilder,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)
from app.schemas.repository_release_attestation import (
    RepositoryReleaseAttestationEvidenceResponse,
    RepositoryReleaseAttestationRequest,
    RepositoryReleaseAttestationResponse,
    RepositoryReleaseAttestationSummaryResponse,
)

router = APIRouter()


def serialize_repository_release_attestation_evidence(
    evidence: RepositoryReleaseAttestationEvidence,
) -> RepositoryReleaseAttestationEvidenceResponse:
    return RepositoryReleaseAttestationEvidenceResponse(
        name=evidence.name,
        passed=evidence.passed,
        severity=evidence.severity,
        message=evidence.message,
    )


def serialize_repository_release_attestation(
    attestation: RepositoryReleaseAttestation,
) -> RepositoryReleaseAttestationResponse:
    summary = RepositoryReleaseAttestationSummaryBuilder().build(
        attestation
    )

    return RepositoryReleaseAttestationResponse(
        schema_version=attestation.schema_version,
        repository_path=attestation.repository_path,
        repository_name=attestation.repository_name,
        attestation_id=attestation.attestation_id,
        attestation_valid=verify_release_attestation(
            attestation
        ),
        certificate_id=attestation.certificate_id,
        certificate_valid=attestation.certificate_valid,
        certified=attestation.certified,
        accepted=attestation.accepted,
        rejected=attestation.rejected,
        status=attestation.status,
        baseline_fingerprint=attestation.baseline_fingerprint,
        candidate_fingerprint=attestation.candidate_fingerprint,
        evidence=[
            serialize_repository_release_attestation_evidence(
                evidence
            )
            for evidence in attestation.evidence
        ],
        evidence_count=attestation.evidence_count,
        passed_evidence_count=(
            attestation.passed_evidence_count
        ),
        failed_evidence_count=(
            attestation.failed_evidence_count
        ),
        evidence_names=attestation.evidence_names,
        issues=attestation.issues,
        issue_count=attestation.issue_count,
        attestation_json=attestation.as_json(),
        summary=RepositoryReleaseAttestationSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-release-attestation",
    response_model=RepositoryReleaseAttestationResponse,
    status_code=status.HTTP_200_OK,
)
def create_repository_release_attestation(
    data: RepositoryReleaseAttestationRequest,
):
    try:
        baseline = RepositorySnapshotBaseline.from_json(
            data.baseline_json
        )

        policy = RepositorySnapshotPolicy(
            require_fingerprint_match=(
                data.policy.require_fingerprint_match
            ),
            allow_added_metrics=data.policy.allow_added_metrics,
            allow_removed_metrics=(
                data.policy.allow_removed_metrics
            ),
            max_warning_delta=data.policy.max_warning_delta,
            max_critical_delta=data.policy.max_critical_delta,
            max_node_decrease=data.policy.max_node_decrease,
            max_edge_decrease=data.policy.max_edge_decrease,
            max_metric_decrease=data.policy.max_metric_decrease,
        )

        attestation = RepositoryReleaseAttestationBuilder().build(
            repository_path=data.repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=data.max_depth,
        )

        return serialize_repository_release_attestation(
            attestation
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
