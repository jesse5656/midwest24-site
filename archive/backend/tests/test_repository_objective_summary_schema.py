from app.schemas.repository_objective_summary import RepositoryObjectiveSummaryResponse


def test_repository_objective_summary_response_accepts_complete_payload():
    response = RepositoryObjectiveSummaryResponse(
        objective_name="Repository Ingestion Observability",
        status="complete",
        total_documents=10,
        total_processing_jobs=10,
        total_failures=0,
        total_duplicates=2,
        total_unsupported=3,
        total_skipped=4,
        action_required=False,
        is_complete=True,
    )

    assert response.objective_name == "Repository Ingestion Observability"
    assert response.is_complete is True


def test_repository_objective_summary_response_serializes_to_dict():
    response = RepositoryObjectiveSummaryResponse(
        objective_name="Repository Ingestion Observability",
        status="attention_required",
        total_documents=1,
        total_processing_jobs=1,
        total_failures=1,
        total_duplicates=0,
        total_unsupported=0,
        total_skipped=0,
        action_required=True,
        is_complete=False,
    )

    payload = response.model_dump()

    assert payload["status"] == "attention_required"
    assert payload["action_required"] is True
    assert payload["is_complete"] is False


def test_repository_objective_summary_response_requires_boolean_completion_state():
    response = RepositoryObjectiveSummaryResponse(
        objective_name="Repository Ingestion Observability",
        status="complete",
        total_documents=0,
        total_processing_jobs=0,
        total_failures=0,
        total_duplicates=0,
        total_unsupported=0,
        total_skipped=0,
        action_required=False,
        is_complete=True,
    )

    assert isinstance(response.is_complete, bool)
