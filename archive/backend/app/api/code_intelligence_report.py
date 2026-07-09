from fastapi import APIRouter, HTTPException, status

from app.api.code_inventory import serialize_code_inventory_preview
from app.api.source_outline import serialize_source_outline_preview
from app.connectors.repository import (
    CodeIntelligenceCloseoutBuilder,
    CodeIntelligenceReport,
    CodeIntelligenceReportBuilder,
    CodeIntelligenceSummaryBuilder,
)
from app.schemas.code_intelligence_report import (
    CodeIntelligenceCloseoutResponse,
    CodeIntelligenceOperatorSummaryResponse,
    CodeIntelligenceReadinessCheckResponse,
    CodeIntelligenceReadinessReportResponse,
    CodeIntelligenceReportRequest,
    CodeIntelligenceReportResponse,
)

router = APIRouter()


def serialize_code_intelligence_readiness(readiness):
    return CodeIntelligenceReadinessReportResponse(
        checks=[
            CodeIntelligenceReadinessCheckResponse(
                name=check.name,
                passed=check.passed,
                message=check.message,
            )
            for check in readiness.checks
        ],
        passed=readiness.passed,
        passed_count=readiness.passed_count,
        failed_count=readiness.failed_count,
    )


def serialize_code_intelligence_report(report: CodeIntelligenceReport) -> CodeIntelligenceReportResponse:
    summary = CodeIntelligenceSummaryBuilder().build(report)
    closeout = CodeIntelligenceCloseoutBuilder().build(report)

    return CodeIntelligenceReportResponse(
        inventory=serialize_code_inventory_preview(report.inventory),
        outline=serialize_source_outline_preview(report.outline),
        file_count=report.file_count,
        language_count=report.language_count,
        symbol_count=report.symbol_count,
        function_count=report.function_count,
        class_count=report.class_count,
        files_with_symbols_count=report.files_with_symbols_count,
        has_inventory=report.has_inventory,
        has_outline=report.has_outline,
        is_ready=report.is_ready,
        summary=CodeIntelligenceOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
        closeout=CodeIntelligenceCloseoutResponse(
            objective_name=closeout.objective_name,
            status=closeout.status,
            can_close=closeout.can_close,
            readiness=serialize_code_intelligence_readiness(closeout.readiness),
            next_action=closeout.next_action,
        ),
    )


@router.post(
    "/api/v1/repository-code-intelligence-report",
    response_model=CodeIntelligenceReportResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_code_intelligence_report(data: CodeIntelligenceReportRequest):
    try:
        report = CodeIntelligenceReportBuilder().build(data.repository_path)
        return serialize_code_intelligence_report(report)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
