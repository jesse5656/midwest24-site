from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_evidence_package import (
    RepositoryReleaseEvidenceItem,
    RepositoryReleaseEvidencePackage,
    RepositoryReleaseEvidencePackageBuilder,
    verify_release_evidence_package,
)
from app.connectors.repository.repository_release_evidence_package_summary import (
    RepositoryReleaseEvidencePackageSummaryBuilder,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)
from app.schemas.repository_release_evidence_package import (
    RepositoryReleaseEvidenceItemResponse,
    RepositoryReleaseEvidencePackageRequest,
    RepositoryReleaseEvidencePackageResponse,
    RepositoryReleaseEvidencePackageSummaryResponse,
)

router = APIRouter()


def serialize_release_evidence_item(
    item: RepositoryReleaseEvidenceItem,
) -> RepositoryReleaseEvidenceItemResponse:
    return RepositoryReleaseEvidenceItemResponse(
        name=item.name,
        status=item.status,
        reference=item.reference,
    )


def serialize_release_evidence_package(
    package: RepositoryReleaseEvidencePackage,
) -> RepositoryReleaseEvidencePackageResponse:
    summary = RepositoryReleaseEvidencePackageSummaryBuilder().build(
        package
    )

    return RepositoryReleaseEvidencePackageResponse(
        schema_version=package.schema_version,
        repository_path=package.repository_path,
        repository_name=package.repository_name,
        package_id=package.package_id,
        package_valid=verify_release_evidence_package(package),
        accepted=package.accepted,
        rejected=package.rejected,
        status=package.status,
        certificate_id=package.certificate.certificate_id,
        certificate_accepted=(
            package.certificate_verification.accepted
        ),
        attestation_id=package.attestation.attestation_id,
        attestation_accepted=(
            package.attestation_verification.accepted
        ),
        baseline_fingerprint=(
            package.certificate.baseline_fingerprint
        ),
        candidate_fingerprint=(
            package.certificate.candidate_fingerprint
        ),
        evidence=[
            serialize_release_evidence_item(item)
            for item in package.evidence
        ],
        evidence_count=package.evidence_count,
        failed_component_count=package.failed_component_count,
        component_names=package.component_names,
        package_json=package.as_json(),
        summary=RepositoryReleaseEvidencePackageSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-release-evidence-package",
    response_model=RepositoryReleaseEvidencePackageResponse,
    status_code=status.HTTP_200_OK,
)
def create_repository_release_evidence_package(
    data: RepositoryReleaseEvidencePackageRequest,
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

        package = RepositoryReleaseEvidencePackageBuilder().build(
            repository_path=data.repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=data.max_depth,
        )

        return serialize_release_evidence_package(package)

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
