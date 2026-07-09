from fastapi import APIRouter, HTTPException, status

from app.connectors.repository import (
    SourceOutlineFile,
    SourceOutlinePreview,
    SourceOutlinePreviewBuilder,
    SourceOutlineSummaryBuilder,
    SourceOutlineSymbol,
)
from app.schemas.source_outline import (
    SourceOutlineFileResponse,
    SourceOutlineOperatorSummaryResponse,
    SourceOutlinePreviewRequest,
    SourceOutlinePreviewResponse,
    SourceOutlineSymbolResponse,
)

router = APIRouter()


def serialize_source_outline_symbol(symbol: SourceOutlineSymbol) -> SourceOutlineSymbolResponse:
    return SourceOutlineSymbolResponse(
        name=symbol.name,
        symbol_type=symbol.symbol_type,
        line_number=symbol.line_number,
    )


def serialize_source_outline_file(file: SourceOutlineFile) -> SourceOutlineFileResponse:
    return SourceOutlineFileResponse(
        path=file.path,
        suffix=file.suffix,
        language=file.language,
        symbols=[serialize_source_outline_symbol(symbol) for symbol in file.symbols],
        symbol_count=file.symbol_count,
        function_count=file.function_count,
        class_count=file.class_count,
    )


def serialize_source_outline_preview(preview: SourceOutlinePreview) -> SourceOutlinePreviewResponse:
    summary = SourceOutlineSummaryBuilder().build(preview)

    return SourceOutlinePreviewResponse(
        file_count=preview.file_count,
        symbol_count=preview.symbol_count,
        function_count=preview.function_count,
        class_count=preview.class_count,
        files_with_symbols_count=len(preview.files_with_symbols),
        files=[serialize_source_outline_file(file) for file in preview.files],
        summary=SourceOutlineOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-source-outline",
    response_model=SourceOutlinePreviewResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_source_outline(data: SourceOutlinePreviewRequest):
    try:
        preview = SourceOutlinePreviewBuilder().build(data.repository_path)
        return serialize_source_outline_preview(preview)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
