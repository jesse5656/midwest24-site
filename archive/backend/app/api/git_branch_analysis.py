from fastapi import APIRouter, HTTPException, status

from app.connectors.repository import (
    GitBranch,
    GitBranchAnalysis,
    GitBranchAnalysisBuilder,
    GitBranchAnalysisSummaryBuilder,
)
from app.schemas.git_branch_analysis import (
    GitBranchAnalysisOperatorSummaryResponse,
    GitBranchAnalysisRequest,
    GitBranchAnalysisResponse,
    GitBranchResponse,
)

router = APIRouter()


def serialize_git_branch(branch: GitBranch | None):
    if branch is None:
        return None

    return GitBranchResponse(name=branch.name, current=branch.current)


def serialize_git_branch_analysis(analysis: GitBranchAnalysis) -> GitBranchAnalysisResponse:
    summary = GitBranchAnalysisSummaryBuilder().build(analysis)

    return GitBranchAnalysisResponse(
        branch_count=analysis.branch_count,
        branches=[serialize_git_branch(branch) for branch in analysis.branches],
        current_branch=serialize_git_branch(analysis.current_branch),
        current_branch_name=analysis.current_branch_name,
        has_multiple_branches=analysis.has_multiple_branches,
        branch_names=analysis.branch_names,
        non_current_branch_names=analysis.non_current_branch_names,
        summary=GitBranchAnalysisOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-git-branch-analysis",
    response_model=GitBranchAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_git_branch_analysis(data: GitBranchAnalysisRequest):
    try:
        analysis = GitBranchAnalysisBuilder().build(data.repository_path)
        return serialize_git_branch_analysis(analysis)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
