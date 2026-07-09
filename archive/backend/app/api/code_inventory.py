from fastapi import APIRouter, HTTPException, status

from app.connectors.repository import (
    CodeInventoryFile,
    CodeInventoryPreview,
    CodeInventoryPreviewBuilder,
    CodeInventorySummaryBuilder,
)
from app.schemas.code_inventory import (
    CodeInventoryFileResponse,
    CodeInventoryLanguageSummaryResponse,
    CodeInventoryOperatorSummaryResponse,
    CodeInventoryPreviewRequest,
    CodeInventoryPreviewResponse,
)

router = APIRouter()


def serialize_code_inventory_file(file: CodeInventoryFile | None):
    if file is None:
        return None

    return CodeInventoryFileResponse(
        path=file.path,
        suffix=file.suffix,
        language=file.language,
        size_bytes=file.size_bytes,
    )


def serialize_code_inventory_preview(preview: CodeInventoryPreview) -> CodeInventoryPreviewResponse:
    summary = CodeInventorySummaryBuilder().build(preview)

    return CodeInventoryPreviewResponse(
        file_count=preview.file_count,
        total_size_bytes=preview.total_size_bytes,
        language_count=preview.language_count,
        languages=preview.languages,
        largest_file=serialize_code_inventory_file(preview.largest_file),
        language_summaries=[
            CodeInventoryLanguageSummaryResponse(
                language=item.language,
                file_count=item.file_count,
                size_bytes=item.size_bytes,
            )
            for item in preview.language_summaries
        ],
        files=[serialize_code_inventory_file(file) for file in preview.files],
        summary=CodeInventoryOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-code-inventory",
    response_model=CodeInventoryPreviewResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_code_inventory(data: CodeInventoryPreviewRequest):
    try:
        preview = CodeInventoryPreviewBuilder().build(data.repository_path)
        return serialize_code_inventory_preview(preview)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
