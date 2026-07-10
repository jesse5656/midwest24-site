from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_semantic_search import (
    RepositorySemanticSearchEngine,
    RepositorySemanticSearchReport,
    RepositorySemanticSearchResult,
)
from app.connectors.repository.repository_semantic_search_summary import (
    RepositorySemanticSearchSummaryBuilder,
)
from app.schemas.repository_semantic_search import (
    RepositorySemanticSearchRequest,
    RepositorySemanticSearchResponse,
    RepositorySemanticSearchResultResponse,
    RepositorySemanticSearchSummaryResponse,
)

router = APIRouter()


def serialize_repository_semantic_search_result(
    result: RepositorySemanticSearchResult,
) -> RepositorySemanticSearchResultResponse:
    return RepositorySemanticSearchResultResponse(
        document_id=result.document_id,
        document_type=result.document_type,
        title=result.title,
        source=result.source,
        lexical_score=result.lexical_score,
        concept_score=result.concept_score,
        total_score=result.total_score,
        matched_terms=result.matched_terms,
    )


def serialize_repository_semantic_search_report(
    report: RepositorySemanticSearchReport,
) -> RepositorySemanticSearchResponse:
    summary = RepositorySemanticSearchSummaryBuilder().build(report)

    return RepositorySemanticSearchResponse(
        repository_path=report.repository_path,
        query=report.query,
        results=[
            serialize_repository_semantic_search_result(result)
            for result in report.results
        ],
        result_count=report.result_count,
        document_types=report.document_types,
        highest_score=report.highest_score,
        summary=RepositorySemanticSearchSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-semantic-search",
    response_model=RepositorySemanticSearchResponse,
    status_code=status.HTTP_200_OK,
)
def search_repository(data: RepositorySemanticSearchRequest):
    try:
        report = RepositorySemanticSearchEngine().search(
            repository_path=data.repository_path,
            query=data.query,
            max_depth=data.max_depth,
            limit=data.limit,
        )
        return serialize_repository_semantic_search_report(report)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except NotADirectoryError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
