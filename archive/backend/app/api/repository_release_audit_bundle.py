from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_audit_bundle import (
    RepositoryReleaseAuditBundle,
    RepositoryReleaseAuditBundleBuilder,
    verify_release_audit_bundle,
)
from app.connectors.repository.repository_release_audit_bundle_summary import (
    RepositoryReleaseAuditBundleSummaryBuilder,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaseline,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)
from app.schemas.repository_release_audit_bundle import (
    RepositoryReleaseAuditBundleRequest,
    RepositoryReleaseAuditBundleResponse,
    RepositoryReleaseAuditBundleSummaryResponse,
)

router = APIRouter()


def serialize_repository_release_audit_bundle(
    bundle: RepositoryReleaseAuditBundle,
) -> RepositoryReleaseAuditBundleResponse:
    summary = RepositoryReleaseAuditBundleSummaryBuilder().build(
        bundle
    )

    return RepositoryReleaseAuditBundleResponse(
        schema_version=bundle.schema_version,
        repository_path=bundle.repository_path,
        repository_name=bundle.repository_name,
        bundle_id=bundle.bundle_id,
        bundle_valid=verify_release_audit_bundle(bundle),
        accepted=bundle.accepted,
        rejected=bundle.rejected,
        status=bundle.status,
        exit_code=bundle.exit_code,
        package_id=bundle.package_id,
        package_accepted=(
            bundle.package_verification.accepted
        ),
        report_id=bundle.report_id,
        report_accepted=(
            bundle.audit_verification.accepted
        ),
        certificate_id=bundle.certificate_id,
        attestation_id=bundle.attestation_id,
        failed_component_count=bundle.failed_component_count,
        component_names=bundle.component_names,
        bundle_json=bundle.as_json(),
        bundle_markdown=bundle.as_markdown(),
        summary=RepositoryReleaseAuditBundleSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-release-audit-bundle",
    response_model=RepositoryReleaseAuditBundleResponse,
    status_code=status.HTTP_200_OK,
)
def create_repository_release_audit_bundle(
    data: RepositoryReleaseAuditBundleRequest,
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

        bundle = RepositoryReleaseAuditBundleBuilder().build(
            repository_path=data.repository_path,
            baseline=baseline,
            policy=policy,
            max_depth=data.max_depth,
        )

        return serialize_repository_release_audit_bundle(
            bundle
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
