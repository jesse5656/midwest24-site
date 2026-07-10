from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_symbol_index import (
    RepositorySymbol,
    RepositorySymbolIndex,
    RepositorySymbolIndexBuilder,
)
from app.connectors.repository.repository_symbol_index_summary import RepositorySymbolIndexSummaryBuilder
from app.schemas.repository_symbol_index import (
    RepositorySymbolIndexRequest,
    RepositorySymbolIndexResponse,
    RepositorySymbolIndexSummaryResponse,
    RepositorySymbolResponse,
)

router = APIRouter()


def serialize_repository_symbol(symbol: RepositorySymbol) -> RepositorySymbolResponse:
    return RepositorySymbolResponse(
        name=symbol.name,
        symbol_type=symbol.symbol_type,
        source_file=symbol.source_file,
        line_number=symbol.line_number,
        parent=symbol.parent,
        qualified_name=symbol.qualified_name,
    )


def serialize_repository_symbol_index(index: RepositorySymbolIndex) -> RepositorySymbolIndexResponse:
    summary = RepositorySymbolIndexSummaryBuilder().build(index)

    return RepositorySymbolIndexResponse(
        repository_path=index.repository_path,
        symbols=[serialize_repository_symbol(symbol) for symbol in index.symbols],
        symbol_count=index.symbol_count,
        source_file_count=index.source_file_count,
        source_files=index.source_files,
        symbol_types=index.symbol_types,
        class_count=index.class_count,
        function_count=index.function_count,
        method_count=index.method_count,
        constant_count=index.constant_count,
        summary=RepositorySymbolIndexSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-symbol-index",
    response_model=RepositorySymbolIndexResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_symbol_index(data: RepositorySymbolIndexRequest):
    try:
        index = RepositorySymbolIndexBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )
        return serialize_repository_symbol_index(index)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
