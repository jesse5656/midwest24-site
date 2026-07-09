from app.api.backend_milestone import (
    serialize_backend_milestone_readiness,
    serialize_backend_milestone_scorecard,
)
from app.connectors.repository import BackendMilestoneReadinessEvaluator, BackendMilestoneScorecardBuilder


def test_serialize_backend_milestone_readiness_maps_counts():
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=721)
    readiness = BackendMilestoneReadinessEvaluator().evaluate(scorecard)

    response = serialize_backend_milestone_readiness(readiness)

    assert response.passed is True
    assert response.failed_count == 0


def test_serialize_backend_milestone_scorecard_maps_counts():
    response = serialize_backend_milestone_scorecard(
        BackendMilestoneScorecardBuilder().build(test_count=721)
    )

    assert response.test_count == 721
    assert response.capability_count == 7
    assert response.completed_capability_count == 7
    assert response.incomplete_capability_count == 0


def test_serialize_backend_milestone_scorecard_maps_summary():
    response = serialize_backend_milestone_scorecard(
        BackendMilestoneScorecardBuilder().build(test_count=721)
    )

    assert response.summary.outcome == "complete"
    assert response.summary.action_required is False


def test_serialize_backend_milestone_scorecard_maps_closeout():
    response = serialize_backend_milestone_scorecard(
        BackendMilestoneScorecardBuilder().build(test_count=721)
    )

    assert response.closeout.status == "ready_to_close"
    assert response.closeout.can_close is True


def test_serialize_backend_milestone_scorecard_maps_capabilities():
    response = serialize_backend_milestone_scorecard(
        BackendMilestoneScorecardBuilder().build(test_count=721)
    )

    names = [capability.name for capability in response.capabilities]

    assert "entity_api" in names
    assert "backend_health" in names
