from app.api.code_objective_scorecard import serialize_code_objective_scorecard
from app.connectors.repository import CodeObjectiveScorecardBuilder


def test_serialize_code_scorecard_maps_counts():
    scorecard = CodeObjectiveScorecardBuilder().build(test_count=645)

    response = serialize_code_objective_scorecard(scorecard)

    assert response.test_count == 645
    assert response.capability_count == 5
    assert response.completed_capability_count == 5
    assert response.incomplete_capability_count == 0


def test_serialize_code_scorecard_maps_capabilities():
    response = serialize_code_objective_scorecard(
        CodeObjectiveScorecardBuilder().build(test_count=645)
    )

    names = [capability.name for capability in response.capabilities]

    assert "code_inventory_api" in names
    assert "source_outline_api" in names


def test_serialize_code_scorecard_maps_completion_ratio():
    response = serialize_code_objective_scorecard(
        CodeObjectiveScorecardBuilder().build(test_count=645)
    )

    assert response.completion_ratio == 1.0
    assert response.is_complete is True


def test_serialize_code_scorecard_maps_summary():
    response = serialize_code_objective_scorecard(
        CodeObjectiveScorecardBuilder().build(test_count=645)
    )

    assert response.summary.outcome == "complete"
    assert response.summary.action_required is False
