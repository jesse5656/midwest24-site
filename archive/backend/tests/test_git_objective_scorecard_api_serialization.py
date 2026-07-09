from app.api.git_objective_scorecard import serialize_git_objective_scorecard
from app.connectors.repository import GitObjectiveScorecardBuilder


def test_serialize_scorecard_maps_counts():
    scorecard = GitObjectiveScorecardBuilder().build(test_count=473)

    response = serialize_git_objective_scorecard(scorecard)

    assert response.test_count == 473
    assert response.capability_count == 7
    assert response.completed_capability_count == 7
    assert response.incomplete_capability_count == 0


def test_serialize_scorecard_maps_capabilities():
    response = serialize_git_objective_scorecard(
        GitObjectiveScorecardBuilder().build(test_count=473)
    )

    names = [capability.name for capability in response.capabilities]

    assert "repository_intelligence_api" in names
    assert "branch_analysis_api" in names


def test_serialize_scorecard_maps_completion_ratio():
    response = serialize_git_objective_scorecard(
        GitObjectiveScorecardBuilder().build(test_count=473)
    )

    assert response.completion_ratio == 1.0
    assert response.is_complete is True


def test_serialize_scorecard_maps_summary():
    response = serialize_git_objective_scorecard(
        GitObjectiveScorecardBuilder().build(test_count=473)
    )

    assert response.summary.outcome == "complete"
    assert response.summary.action_required is False
