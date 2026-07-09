import pytest
from pydantic import ValidationError

from app.schemas.repository_progress import (
    RepositoryProgressCheckpointRequest,
    RepositoryProgressCheckpointResponse,
    RepositoryProgressLedgerResponse,
    RepositoryProgressSummaryResponse,
)


def test_progress_checkpoint_request_accepts_payload():
    request = RepositoryProgressCheckpointRequest(
        name="Checkpoint",
        test_count=443,
        status="completed",
    )

    assert request.notes == ""


def test_progress_checkpoint_request_rejects_empty_name():
    with pytest.raises(ValidationError):
        RepositoryProgressCheckpointRequest(name="", test_count=1, status="completed")


def test_progress_checkpoint_request_rejects_negative_test_count():
    with pytest.raises(ValidationError):
        RepositoryProgressCheckpointRequest(name="A", test_count=-1, status="completed")


def test_progress_checkpoint_response_accepts_payload():
    response = RepositoryProgressCheckpointResponse(
        name="A",
        test_count=1,
        status="completed",
        notes="ok",
    )

    assert response.notes == "ok"


def test_progress_ledger_response_accepts_payload():
    response = RepositoryProgressLedgerResponse(
        repository="midwest24-site",
        checkpoints=[
            RepositoryProgressCheckpointResponse(
                name="A",
                test_count=1,
                status="completed",
                notes="ok",
            )
        ],
        latest_test_count=1,
        checkpoint_count=1,
        completed_count=1,
    )

    assert response.latest_test_count == 1


def test_progress_summary_response_accepts_payload():
    response = RepositoryProgressSummaryResponse(
        repository="midwest24-site",
        latest_test_count=443,
        checkpoint_count=10,
        completed_count=9,
        status="completed",
        message="ok",
    )

    assert response.repository == "midwest24-site"
    assert response.latest_test_count == 443
