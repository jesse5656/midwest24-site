import pytest
from pydantic import ValidationError

from app.schemas.code_inventory import (
    CodeInventoryFileResponse,
    CodeInventoryLanguageSummaryResponse,
    CodeInventoryOperatorSummaryResponse,
    CodeInventoryPreviewRequest,
    CodeInventoryPreviewResponse,
)


def test_code_inventory_request_accepts_path():
    request = CodeInventoryPreviewRequest(repository_path="/repo")

    assert request.repository_path == "/repo"


def test_code_inventory_request_rejects_empty_path():
    with pytest.raises(ValidationError):
        CodeInventoryPreviewRequest(repository_path="")


def test_code_inventory_file_response_accepts_payload():
    response = CodeInventoryFileResponse(
        path="main.py",
        suffix=".py",
        language="Python",
        size_bytes=10,
    )

    assert response.language == "Python"


def test_code_inventory_language_summary_response_accepts_payload():
    response = CodeInventoryLanguageSummaryResponse(
        language="Python",
        file_count=2,
        size_bytes=30,
    )

    assert response.file_count == 2


def test_code_inventory_summary_response_accepts_payload():
    response = CodeInventoryOperatorSummaryResponse(
        outcome="multi_language_inventory",
        message="ok",
        action_required=False,
    )

    assert response.outcome == "multi_language_inventory"


def test_code_inventory_preview_response_serializes_nested_payload():
    file_response = CodeInventoryFileResponse(
        path="main.py",
        suffix=".py",
        language="Python",
        size_bytes=10,
    )

    response = CodeInventoryPreviewResponse(
        file_count=1,
        total_size_bytes=10,
        language_count=1,
        languages=["Python"],
        largest_file=file_response,
        language_summaries=[
            CodeInventoryLanguageSummaryResponse(
                language="Python",
                file_count=1,
                size_bytes=10,
            )
        ],
        files=[file_response],
        summary=CodeInventoryOperatorSummaryResponse(
            outcome="single_language_inventory",
            message="ok",
            action_required=False,
        ),
    )

    payload = response.model_dump()

    assert payload["largest_file"]["path"] == "main.py"
    assert payload["language_summaries"][0]["language"] == "Python"
