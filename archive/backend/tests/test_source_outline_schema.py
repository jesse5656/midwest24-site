import pytest
from pydantic import ValidationError

from app.schemas.source_outline import (
    SourceOutlineFileResponse,
    SourceOutlineOperatorSummaryResponse,
    SourceOutlinePreviewRequest,
    SourceOutlinePreviewResponse,
    SourceOutlineSymbolResponse,
)


def test_source_outline_request_accepts_path():
    request = SourceOutlinePreviewRequest(repository_path="/repo")

    assert request.repository_path == "/repo"


def test_source_outline_request_rejects_empty_path():
    with pytest.raises(ValidationError):
        SourceOutlinePreviewRequest(repository_path="")


def test_source_outline_symbol_response_accepts_payload():
    response = SourceOutlineSymbolResponse(
        name="run",
        symbol_type="function",
        line_number=1,
    )

    assert response.name == "run"


def test_source_outline_file_response_accepts_payload():
    response = SourceOutlineFileResponse(
        path="main.py",
        suffix=".py",
        language="Python",
        symbols=[
            SourceOutlineSymbolResponse(
                name="run",
                symbol_type="function",
                line_number=1,
            )
        ],
        symbol_count=1,
        function_count=1,
        class_count=0,
    )

    assert response.symbol_count == 1


def test_source_outline_summary_response_accepts_payload():
    response = SourceOutlineOperatorSummaryResponse(
        outcome="symbols_found",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "symbols_found"


def test_source_outline_preview_response_serializes_nested_payload():
    file_response = SourceOutlineFileResponse(
        path="main.py",
        suffix=".py",
        language="Python",
        symbols=[
            SourceOutlineSymbolResponse(
                name="run",
                symbol_type="function",
                line_number=1,
            )
        ],
        symbol_count=1,
        function_count=1,
        class_count=0,
    )

    response = SourceOutlinePreviewResponse(
        file_count=1,
        symbol_count=1,
        function_count=1,
        class_count=0,
        files_with_symbols_count=1,
        files=[file_response],
        summary=SourceOutlineOperatorSummaryResponse(
            outcome="symbols_found",
            message="ok",
            action_required=False,
        ),
    )

    payload = response.model_dump()

    assert payload["files"][0]["symbols"][0]["name"] == "run"
