from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_search_index import (
    RepositorySearchDocument,
    RepositorySearchIndex,
    RepositorySearchIndexBuilder,
    RepositorySearchResult,
)
from app.connectors.repository.repository_search_index_summary import (
    RepositorySearchIndexSummaryBuilder,
)
from app.schemas.repository_search_index import (
    RepositorySearchDocumentResponse,
    RepositorySearchIndexRequest,
    RepositorySearchIndexResponse,
    RepositorySearchIndexSummaryResponse,
    RepositorySearchResultResponse,
)

router = APIRouter()


def serialize_repository_search_document(
    document: RepositorySearchDocument,
) -> RepositorySearchDocumentResponse:
    return RepositorySearchDocumentResponse(
        document_id=document.document_id,
        document_type=document.document_type,
        title=document.title,
        body=document.body,
        source=document.source,
    )


def serialize_repository_search_result(
    result: RepositorySearchResult,
) -> RepositorySearchResultResponse:
    return RepositorySearchResultResponse(
        document_id=result.document_id,
        document_type=result.document_type,
        title=result.title,
        source=result.source,
        score=result.score,
    )


def serialize_repository_search_index(
    index: RepositorySearchIndex,
    query: str = "",
    limit: int = 10,
) -> RepositorySearchIndexResponse:
    summary = RepositorySearchIndexSummaryBuilder().build(index)

    results = index.search(
        query=query,
        limit=limit,
    ) if query.strip() else []

    return RepositorySearchIndexResponse(
        repository_path=index.repository_path,
        documents=[
            serialize_repository_search_document(document)
            for document in index.documents
        ],
        document_count=index.document_count,
        document_types=index.document_types,
        results=[
            serialize_repository_search_result(result)
            for result in results
        ],
        result_count=len(results),
        summary=RepositorySearchIndexSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-search-index",
    response_model=RepositorySearchIndexResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_search_index(
    data: RepositorySearchIndexRequest,
):
    try:
        index = RepositorySearchIndexBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )

        return serialize_repository_search_index(
            index=index,
            query=data.query,
            limit=data.limit,
        )

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
