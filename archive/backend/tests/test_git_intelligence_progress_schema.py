from app.schemas.git_intelligence_progress import GitIntelligenceProgressResponse


def test_git_intelligence_progress_response_accepts_payload():
    response = GitIntelligenceProgressResponse(
        objective_name="Git Repository Intelligence",
        capability_count=5,
        endpoint_count=5,
        test_count=443,
        status="completed",
        ready_for_closeout=True,
    )

    assert response.ready_for_closeout is True


def test_git_intelligence_progress_response_serializes_payload():
    response = GitIntelligenceProgressResponse(
        objective_name="Git Repository Intelligence",
        capability_count=4,
        endpoint_count=5,
        test_count=443,
        status="in_progress",
        ready_for_closeout=False,
    )

    payload = response.model_dump()

    assert payload["status"] == "in_progress"
    assert payload["ready_for_closeout"] is False
