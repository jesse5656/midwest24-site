from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_release_audit_report import (
    RepositoryReleaseAuditFinding,
    RepositoryReleaseAuditReport,
    RepositoryReleaseAuditReportBuilder,
    verify_release_audit_report,
)
from app.connectors.repository.repository_release_audit_report_summary import (
    RepositoryReleaseAuditReportSummaryBuilder,
)
from app.schemas.repository_release_audit_report import (
    RepositoryReleaseAuditFindingResponse,
    RepositoryReleaseAuditReportRequest,
    RepositoryReleaseAuditReportResponse,
    RepositoryReleaseAuditReportSummaryResponse,
)

router = APIRouter()


def serialize_repository_release_audit_finding(
    finding: RepositoryReleaseAuditFinding,
) -> RepositoryReleaseAuditFindingResponse:
    return RepositoryReleaseAuditFindingResponse(
        code=finding.code,
        severity=finding.severity,
        message=finding.message,
    )


def serialize_repository_release_audit_report(
    report: RepositoryReleaseAuditReport,
) -> RepositoryReleaseAuditReportResponse:
    summary = RepositoryReleaseAuditReportSummaryBuilder().build(
        report
    )

    return RepositoryReleaseAuditReportResponse(
        schema_version=report.schema_version,
        report_id=report.report_id,
        report_valid=verify_release_audit_report(report),
        package_id=report.package_id,
        repository_name=report.repository_name,
        accepted=report.accepted,
        integrity_valid=report.integrity_valid,
        passed=report.passed,
        failed=report.failed,
        exit_code=report.exit_code,
        status=report.status,
        certificate_id=report.certificate_id,
        attestation_id=report.attestation_id,
        findings=[
            serialize_repository_release_audit_finding(
                finding
            )
            for finding in report.findings
        ],
        finding_count=report.finding_count,
        critical_finding_count=(
            report.critical_finding_count
        ),
        error_finding_count=report.error_finding_count,
        warning_finding_count=(
            report.warning_finding_count
        ),
        finding_codes=report.finding_codes,
        report_json=report.as_json(),
        report_markdown=report.as_markdown(),
        summary=RepositoryReleaseAuditReportSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-release-audit-report",
    response_model=RepositoryReleaseAuditReportResponse,
    status_code=status.HTTP_200_OK,
)
def create_repository_release_audit_report(
    data: RepositoryReleaseAuditReportRequest,
):
    try:
        report = RepositoryReleaseAuditReportBuilder().build(
            package_json=data.package_json,
            require_accepted=data.require_accepted,
            expected_certificate_id=(
                data.expected_certificate_id
            ),
            expected_attestation_id=(
                data.expected_attestation_id
            ),
            expected_baseline_fingerprint=(
                data.expected_baseline_fingerprint
            ),
            expected_candidate_fingerprint=(
                data.expected_candidate_fingerprint
            ),
        )

        return serialize_repository_release_audit_report(
            report
        )

    except (
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
