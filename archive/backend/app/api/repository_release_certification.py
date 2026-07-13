from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_certification import (
    RepositoryReleaseCertification,
    RepositoryReleaseCertificationBuilder,
    RepositoryReleaseCertificationEvidence,
    verify_release_certificate,
)
from app.connectors.repository.repository_release_certification_summary import (
    RepositoryReleaseCertificationSummaryBuilder,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)
from app.schemas.repository_release_certification import (
    RepositoryReleaseCertificationEvidenceResponse,
    RepositoryReleaseCertificationRequest,
    RepositoryReleaseCertificationResponse,
    RepositoryReleaseCertificationSummaryResponse,
)

router = APIRouter()


def serialize_repository_release_certification_evidence(
    evidence: RepositoryReleaseCertificationEvidence,
) -> RepositoryReleaseCertificationEvidenceResponse:
    return RepositoryReleaseCertificationEvidenceResponse(
        name=evidence.name,
        passed=evidence.passed,
        severity=evidence.severity,
        message=evidence.message,
    )


def serialize_repository_release_certification(
    certification: RepositoryReleaseCertification,
) -> RepositoryReleaseCertificationResponse:
    summary = RepositoryReleaseCertificationSummaryBuilder().build(
        certification
    )

    return RepositoryReleaseCertificationResponse(
        schema_version=certification.schema_version,
        repository_path=certification.repository_path,
        repository_name=certification.repository_name,
        release_ready=certification.release_ready,
        certified=certification.certified,
        denied=certification.denied,
        status=certification.status,
        certificate_id=certification.certificate_id,
        certificate_valid=verify_release_certificate(
            certification
        ),
        baseline_fingerprint=certification.baseline_fingerprint,
        candidate_fingerprint=certification.candidate_fingerprint,
        evidence=[
            serialize_repository_release_certification_evidence(
                evidence
            )
            for evidence in certification.evidence
        ],
        evidence_count=certification.evidence_count,
        passed_evidence_count=(
            certification.passed_evidence_count
        ),
        failed_evidence_count=(
            certification.failed_evidence_count
        ),
        critical_failure_count=(
            certification.critical_failure_count
        ),
        denial_reasons=certification.denial_reasons,
        denial_reason_count=certification.denial_reason_count,
        evidence_names=certification.evidence_names,
        certificate_json=certification.as_json(),
        summary=RepositoryReleaseCertificationSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-release-certification",
    response_model=RepositoryReleaseCertificationResponse,
    status_code=status.HTTP_200_OK,
)
def create_repository_release_certification(
    data: RepositoryReleaseCertificationRequest,
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

        certification = (
            RepositoryReleaseCertificationBuilder()
            .build(
                repository_path=data.repository_path,
                baseline=baseline,
                policy=policy,
                max_depth=data.max_depth,
            )
        )

        return serialize_repository_release_certification(
            certification
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
