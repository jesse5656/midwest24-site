import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.operator_progress_target import (
    serialize_operator_progress_milestone,
    serialize_operator_progress_plan,
    serialize_operator_progress_target,
)
from app.connectors.repository.operator_progress_summary import OperatorProgressSummaryBuilder
from app.connectors.repository.operator_progress_target import (
    OperatorProgressMilestone,
    OperatorProgressPlan,
    OperatorProgressTarget,
    OperatorProgressTargetBuilder,
)
from app.main import app
from app.schemas.operator_progress_target import OperatorProgressTargetRequest

client = TestClient(app)


def make_plan():
    return OperatorProgressTargetBuilder().build(940, 1000)


def test_operator_progress_001_target_delta():
    assert OperatorProgressTarget(940, 1000).delta == 60


def test_operator_progress_002_target_valid():
    assert OperatorProgressTarget(940, 1000).is_valid is True


def test_operator_progress_003_target_invalid_equal():
    assert OperatorProgressTarget(1000, 1000).is_valid is False


def test_operator_progress_004_target_invalid_lower():
    assert OperatorProgressTarget(1000, 940).is_valid is False


def test_operator_progress_005_percent_complete():
    assert OperatorProgressTarget(500, 1000).percent_complete == 0.5


def test_operator_progress_006_percent_complete_caps_at_one():
    assert OperatorProgressTarget(1200, 1000).percent_complete == 1.0


def test_operator_progress_007_percent_complete_zero_target():
    assert OperatorProgressTarget(0, 0).percent_complete == 0.0


def test_operator_progress_008_remaining_tests():
    assert OperatorProgressTarget(940, 1000).remaining_tests == 60


def test_operator_progress_009_remaining_tests_never_negative():
    assert OperatorProgressTarget(1000, 940).remaining_tests == 0


def test_operator_progress_010_builder_milestone_count():
    assert make_plan().milestone_count == 4


def test_operator_progress_011_builder_reached_count():
    assert make_plan().reached_count == 1


def test_operator_progress_012_builder_unreached_count():
    assert make_plan().unreached_count == 3


def test_operator_progress_013_builder_next_milestone():
    assert make_plan().next_milestone.test_count == 960


def test_operator_progress_014_builder_first_milestone_reached():
    assert make_plan().milestones[0].reached is True


def test_operator_progress_015_builder_last_milestone_target():
    assert make_plan().milestones[-1].test_count == 1000


def test_operator_progress_016_builder_deduplicates_close_target():
    plan = OperatorProgressTargetBuilder().build(990, 1000)
    counts = [milestone.test_count for milestone in plan.milestones]
    assert counts == [990, 1000]


def test_operator_progress_017_plan_no_next_milestone_when_all_reached():
    plan = OperatorProgressPlan(
        target=OperatorProgressTarget(1000, 1000),
        milestones=[
            OperatorProgressMilestone("1000_tests", 1000, True),
        ],
    )
    assert plan.next_milestone is None


def test_operator_progress_018_summary_invalid_target():
    plan = OperatorProgressTargetBuilder().build(1000, 940)
    summary = OperatorProgressSummaryBuilder().build(plan)
    assert summary.outcome == "invalid_target"


def test_operator_progress_019_summary_invalid_target_requires_action():
    plan = OperatorProgressTargetBuilder().build(1000, 940)
    summary = OperatorProgressSummaryBuilder().build(plan)
    assert summary.action_required is True


def test_operator_progress_020_summary_in_progress():
    summary = OperatorProgressSummaryBuilder().build(make_plan())
    assert summary.outcome == "in_progress"


def test_operator_progress_021_summary_in_progress_no_action():
    summary = OperatorProgressSummaryBuilder().build(make_plan())
    assert summary.action_required is False


def test_operator_progress_022_summary_mentions_remaining():
    summary = OperatorProgressSummaryBuilder().build(make_plan())
    assert "60 test" in summary.message


def test_operator_progress_023_summary_mentions_next_milestone():
    summary = OperatorProgressSummaryBuilder().build(make_plan())
    assert "960" in summary.message


def test_operator_progress_024_summary_complete():
    plan = OperatorProgressPlan(
        target=OperatorProgressTarget(1000, 1000),
        milestones=[OperatorProgressMilestone("1000_tests", 1000, True)],
    )
    summary = OperatorProgressSummaryBuilder().build(plan)
    assert summary.outcome == "invalid_target"


def test_operator_progress_025_request_accepts_counts():
    request = OperatorProgressTargetRequest(current_test_count=940, target_test_count=1000)
    assert request.current_test_count == 940


def test_operator_progress_026_request_rejects_negative_current():
    with pytest.raises(ValidationError):
        OperatorProgressTargetRequest(current_test_count=-1, target_test_count=1000)


def test_operator_progress_027_request_rejects_negative_target():
    with pytest.raises(ValidationError):
        OperatorProgressTargetRequest(current_test_count=940, target_test_count=-1)


def test_operator_progress_028_serialize_target_delta():
    response = serialize_operator_progress_target(OperatorProgressTarget(940, 1000))
    assert response.delta == 60


def test_operator_progress_029_serialize_target_percent():
    response = serialize_operator_progress_target(OperatorProgressTarget(500, 1000))
    assert response.percent_complete == 0.5


def test_operator_progress_030_serialize_milestone_none():
    assert serialize_operator_progress_milestone(None) is None


def test_operator_progress_031_serialize_milestone_fields():
    response = serialize_operator_progress_milestone(
        OperatorProgressMilestone("960_tests", 960, False)
    )
    assert response.name == "960_tests"


def test_operator_progress_032_serialize_plan_counts():
    response = serialize_operator_progress_plan(make_plan())
    assert response.milestone_count == 4
    assert response.reached_count == 1
    assert response.unreached_count == 3


def test_operator_progress_033_serialize_plan_next_milestone():
    response = serialize_operator_progress_plan(make_plan())
    assert response.next_milestone.test_count == 960


def test_operator_progress_034_serialize_plan_summary():
    response = serialize_operator_progress_plan(make_plan())
    assert response.summary.outcome == "in_progress"


def test_operator_progress_035_api_returns_200():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert response.status_code == 200


def test_operator_progress_036_api_returns_delta():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert response.json()["target"]["delta"] == 60


def test_operator_progress_037_api_returns_remaining():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert response.json()["target"]["remaining_tests"] == 60


def test_operator_progress_038_api_returns_milestones():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert len(response.json()["milestones"]) == 4


def test_operator_progress_039_api_returns_next_milestone():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert response.json()["next_milestone"]["test_count"] == 960


def test_operator_progress_040_api_returns_summary():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert response.json()["summary"]["outcome"] == "in_progress"


def test_operator_progress_041_api_invalid_target():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 1000, "target_test_count": 940},
    )
    assert response.json()["summary"]["outcome"] == "invalid_target"


def test_operator_progress_042_api_rejects_negative_current():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": -1, "target_test_count": 1000},
    )
    assert response.status_code == 422


def test_operator_progress_043_api_rejects_missing_target():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940},
    )
    assert response.status_code == 422


def test_operator_progress_044_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/operator-progress-target" in paths


def test_operator_progress_045_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/operator-progress-target")
    assert "POST" in route.methods


def test_operator_progress_046_milestone_preserves_reached():
    milestone = OperatorProgressMilestone("test", 1, True)
    assert milestone.reached is True


def test_operator_progress_047_plan_counts_empty_milestones():
    plan = OperatorProgressPlan(OperatorProgressTarget(1, 2), [])
    assert plan.milestone_count == 0
    assert plan.reached_count == 0
    assert plan.unreached_count == 0


def test_operator_progress_048_plan_next_milestone_empty():
    plan = OperatorProgressPlan(OperatorProgressTarget(1, 2), [])
    assert plan.next_milestone is None


def test_operator_progress_049_builder_target_current_count():
    assert make_plan().target.current_test_count == 940


def test_operator_progress_050_builder_target_target_count():
    assert make_plan().target.target_test_count == 1000


def test_operator_progress_051_builder_milestone_names():
    names = [milestone.name for milestone in make_plan().milestones]
    assert "940_tests" in names
    assert "1000_tests" in names


def test_operator_progress_052_summary_invalid_target_message():
    plan = OperatorProgressTargetBuilder().build(1000, 940)
    summary = OperatorProgressSummaryBuilder().build(plan)
    assert "greater than current" in summary.message


def test_operator_progress_053_api_percent_complete():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert response.json()["target"]["percent_complete"] == 0.94


def test_operator_progress_054_api_forward_progress_true():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert response.json()["target"]["is_valid"] is True


def test_operator_progress_055_api_forward_progress_false():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 1000, "target_test_count": 940},
    )
    assert response.json()["target"]["is_valid"] is False


def test_operator_progress_056_api_reached_count():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert response.json()["reached_count"] == 1


def test_operator_progress_057_api_unreached_count():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert response.json()["unreached_count"] == 3


def test_operator_progress_058_api_milestone_reached_flags():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert response.json()["milestones"][0]["reached"] is True
    assert response.json()["milestones"][1]["reached"] is False


def test_operator_progress_059_api_close_target_deduplicates():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 990, "target_test_count": 1000},
    )
    assert [m["test_count"] for m in response.json()["milestones"]] == [990, 1000]


def test_operator_progress_060_api_summary_mentions_1000():
    response = client.post(
        "/api/v1/operator-progress-target",
        json={"current_test_count": 940, "target_test_count": 1000},
    )
    assert "1000" in response.json()["summary"]["message"]
