from fastapi import APIRouter, HTTPException, status

from app.api.git_authorship_preview import serialize_git_authorship_preview
from app.api.git_commit_preview import serialize_git_commit_preview
from app.api.git_file_change_preview import serialize_git_file_change_preview
from app.api.git_repository_intelligence import serialize_git_repository_summary
from app.connectors.repository import (
    GitIntelligenceCloseoutBuilder,
    GitIntelligenceReport,
    GitIntelligenceReportBuilder,
    GitIntelligenceSummaryBuilder,
)
from app.schemas.git_intelligence_report import (
    GitIntelligenceCloseoutResponse,
    GitIntelligenceOperatorSummaryResponse,
    GitIntelligenceReadinessCheckResponse,
    GitIntelligenceReadinessReportResponse,
    GitIntelligenceReportRequest,
    GitIntelligenceReportResponse,
)

router = APIRouter()


def serialize_git_intelligence_readiness(readiness):
    return GitIntelligenceReadinessReportResponse(
        checks=[
            GitIntelligenceReadinessCheckResponse(
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


def serialize_git_intelligence_report(report: GitIntelligenceReport) -> GitIntelligenceReportResponse:
    summary = GitIntelligenceSummaryBuilder().build(report)
    closeout = GitIntelligenceCloseoutBuilder().build(report)

    return GitIntelligenceReportResponse(
        repository=serialize_git_repository_summary(report.repository),
        commits=serialize_git_commit_preview(report.commits),
        file_changes=serialize_git_file_change_preview(report.file_changes),
        authorship=serialize_git_authorship_preview(report.authorship),
        is_repository=report.is_repository,
        current_branch=report.current_branch,
        commit_count=report.commit_count,
        file_change_count=report.file_change_count,
        author_count=report.author_count,
        has_uncommitted_changes=report.has_uncommitted_changes,
        is_ready=report.is_ready,
        summary=GitIntelligenceOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
        closeout=GitIntelligenceCloseoutResponse(
            objective_name=closeout.objective_name,
            status=closeout.status,
            can_close=closeout.can_close,
            readiness=serialize_git_intelligence_readiness(closeout.readiness),
            next_action=closeout.next_action,
        ),
    )


@router.post(
    "/api/v1/repository-git-intelligence-report",
    response_model=GitIntelligenceReportResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_git_intelligence_report(data: GitIntelligenceReportRequest):
    try:
        report = GitIntelligenceReportBuilder().build(
            repository_path=data.repository_path,
            limit=data.limit,
        )
        return serialize_git_intelligence_report(report)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
