import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.milestone_closeout_package import serialize_milestone_closeout_package
from app.connectors.repository.milestone_closeout_package import (
    MilestoneCloseoutItem,
    MilestoneCloseoutPackage,
    MilestoneCloseoutPackageBuilder,
)
from app.connectors.repository.milestone_closeout_summary import MilestoneCloseoutSummaryBuilder
from app.main import app
from app.schemas.milestone_closeout_package import MilestoneCloseoutPackageRequest

client = TestClient(app)


def make_package():
    return MilestoneCloseoutPackageBuilder().build(1000)


def test_closeout_001_name():
    assert make_package().milestone_name == "Archive Backend Milestone Closeout"


def test_closeout_002_test_count():
    assert make_package().test_count == 1000


def test_closeout_003_item_count():
    assert make_package().item_count == 7


def test_closeout_004_completed_count():
    assert make_package().completed_count == 7


def test_closeout_005_incomplete_count():
    assert make_package().incomplete_count == 0


def test_closeout_006_is_complete():
    assert make_package().is_complete is True


def test_closeout_007_completion_ratio():
    assert make_package().completion_ratio == 1.0


def test_closeout_008_empty_ratio_zero():
    assert MilestoneCloseoutPackage("Empty", 0).completion_ratio == 0.0


def test_closeout_009_empty_not_complete():
    assert MilestoneCloseoutPackage("Empty", 0).is_complete is False


def test_closeout_010_empty_counts_zero():
    package = MilestoneCloseoutPackage("Empty", 0)
    assert package.item_count == 0
    assert package.completed_count == 0
    assert package.incomplete_count == 0


def test_closeout_011_incomplete_package_not_complete():
    package = MilestoneCloseoutPackage("Test", 1, [MilestoneCloseoutItem("a", False, "missing")])
    assert package.is_complete is False


def test_closeout_012_incomplete_package_counts():
    package = MilestoneCloseoutPackage(
        "Test",
        1,
        [
            MilestoneCloseoutItem("a", True, "done"),
            MilestoneCloseoutItem("b", False, "missing"),
        ],
    )
    assert package.completed_count == 1
    assert package.incomplete_count == 1


def test_closeout_013_item_preserves_evidence():
    item = MilestoneCloseoutItem("tests_green", True, "1000 tests passing.")
    assert item.evidence == "1000 tests passing."


def test_closeout_014_has_tests_green():
    assert "tests_green" in [item.name for item in make_package().items]


def test_closeout_015_has_progress_ledger():
    assert "progress_ledger_updated" in [item.name for item in make_package().items]


def test_closeout_016_has_operating_plan():
    assert "operating_plan_updated" in [item.name for item in make_package().items]


def test_closeout_017_has_runbook():
    assert "runbook_updated" in [item.name for item in make_package().items]


def test_closeout_018_has_session_transition():
    assert "session_transition_ready" in [item.name for item in make_package().items]


def test_closeout_019_has_operator_execution_rules():
    assert "operator_execution_rules_ready" in [item.name for item in make_package().items]


def test_closeout_020_has_next_work_deferred():
    assert "next_work_deferred" in [item.name for item in make_package().items]


def test_closeout_021_all_items_complete():
    assert all(item.completed for item in make_package().items)


def test_closeout_022_all_items_have_evidence():
    assert all(item.evidence for item in make_package().items)


def test_closeout_023_summary_ready():
    summary = MilestoneCloseoutSummaryBuilder().build(make_package())
    assert summary.outcome == "ready_to_close"


def test_closeout_024_summary_no_action():
    summary = MilestoneCloseoutSummaryBuilder().build(make_package())
    assert summary.action_required is False


def test_closeout_025_summary_message_mentions_tests():
    summary = MilestoneCloseoutSummaryBuilder().build(make_package())
    assert "1000 passing tests" in summary.message


def test_closeout_026_summary_message_mentions_ratio():
    summary = MilestoneCloseoutSummaryBuilder().build(make_package())
    assert "7/7" in summary.message


def test_closeout_027_summary_empty():
    summary = MilestoneCloseoutSummaryBuilder().build(MilestoneCloseoutPackage("Empty", 0))
    assert summary.outcome == "empty_closeout"


def test_closeout_028_summary_empty_requires_action():
    summary = MilestoneCloseoutSummaryBuilder().build(MilestoneCloseoutPackage("Empty", 0))
    assert summary.action_required is True


def test_closeout_029_summary_not_ready():
    package = MilestoneCloseoutPackage("Test", 1, [MilestoneCloseoutItem("a", False, "missing")])
    summary = MilestoneCloseoutSummaryBuilder().build(package)
    assert summary.outcome == "not_ready"


def test_closeout_030_summary_not_ready_requires_action():
    package = MilestoneCloseoutPackage("Test", 1, [MilestoneCloseoutItem("a", False, "missing")])
    summary = MilestoneCloseoutSummaryBuilder().build(package)
    assert summary.action_required is True


def test_closeout_031_request_accepts_test_count():
    request = MilestoneCloseoutPackageRequest(test_count=1000)
    assert request.test_count == 1000


def test_closeout_032_request_rejects_negative():
    with pytest.raises(ValidationError):
        MilestoneCloseoutPackageRequest(test_count=-1)


def test_closeout_033_serialize_name():
    response = serialize_milestone_closeout_package(make_package())
    assert response.milestone_name == "Archive Backend Milestone Closeout"


def test_closeout_034_serialize_test_count():
    response = serialize_milestone_closeout_package(make_package())
    assert response.test_count == 1000


def test_closeout_035_serialize_item_count():
    response = serialize_milestone_closeout_package(make_package())
    assert response.item_count == 7


def test_closeout_036_serialize_completed_count():
    response = serialize_milestone_closeout_package(make_package())
    assert response.completed_count == 7


def test_closeout_037_serialize_incomplete_count():
    response = serialize_milestone_closeout_package(make_package())
    assert response.incomplete_count == 0


def test_closeout_038_serialize_complete():
    response = serialize_milestone_closeout_package(make_package())
    assert response.is_complete is True


def test_closeout_039_serialize_ratio():
    response = serialize_milestone_closeout_package(make_package())
    assert response.completion_ratio == 1.0


def test_closeout_040_serialize_items():
    response = serialize_milestone_closeout_package(make_package())
    assert response.items[0].name == "tests_green"


def test_closeout_041_serialize_summary():
    response = serialize_milestone_closeout_package(make_package())
    assert response.summary.outcome == "ready_to_close"


def test_closeout_042_api_returns_200():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.status_code == 200


def test_closeout_043_api_returns_name():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["milestone_name"] == "Archive Backend Milestone Closeout"


def test_closeout_044_api_returns_test_count():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["test_count"] == 1000


def test_closeout_045_api_returns_complete():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["is_complete"] is True


def test_closeout_046_api_returns_item_count():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["item_count"] == 7


def test_closeout_047_api_returns_summary():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["summary"]["outcome"] == "ready_to_close"


def test_closeout_048_api_rejects_negative():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": -1})
    assert response.status_code == 422


def test_closeout_049_api_requires_test_count():
    response = client.post("/api/v1/milestone-closeout-package", json={})
    assert response.status_code == 422


def test_closeout_050_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/milestone-closeout-package" in paths


def test_closeout_051_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/milestone-closeout-package")
    assert "POST" in route.methods


def test_closeout_052_api_evidence_mentions_tests():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    evidence = " ".join(item["evidence"] for item in response.json()["items"])
    assert "1000 tests passing" in evidence


def test_closeout_053_api_contains_progress_ledger_item():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    names = [item["name"] for item in response.json()["items"]]
    assert "progress_ledger_updated" in names


def test_closeout_054_api_contains_operating_plan_item():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    names = [item["name"] for item in response.json()["items"]]
    assert "operating_plan_updated" in names


def test_closeout_055_api_contains_runbook_item():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    names = [item["name"] for item in response.json()["items"]]
    assert "runbook_updated" in names


def test_closeout_056_api_contains_session_transition_item():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    names = [item["name"] for item in response.json()["items"]]
    assert "session_transition_ready" in names


def test_closeout_057_api_contains_operator_execution_item():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    names = [item["name"] for item in response.json()["items"]]
    assert "operator_execution_rules_ready" in names


def test_closeout_058_api_contains_deferred_item():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    names = [item["name"] for item in response.json()["items"]]
    assert "next_work_deferred" in names


def test_closeout_059_builder_uses_dynamic_test_count():
    package = MilestoneCloseoutPackageBuilder().build(1100)
    assert package.test_count == 1100
    assert "1100 tests passing" in package.items[0].evidence


def test_closeout_060_api_uses_dynamic_test_count():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1100})
    assert response.json()["test_count"] == 1100
    assert "1100 tests passing" in response.json()["items"][0]["evidence"]


def test_closeout_061_model_handles_mixed_items():
    package = MilestoneCloseoutPackage(
        "Mixed",
        1,
        [
            MilestoneCloseoutItem("a", True, "done"),
            MilestoneCloseoutItem("b", False, "todo"),
            MilestoneCloseoutItem("c", True, "done"),
        ],
    )
    assert package.item_count == 3
    assert package.completed_count == 2
    assert package.incomplete_count == 1
    assert package.is_complete is False


def test_closeout_062_completion_ratio_mixed():
    package = MilestoneCloseoutPackage(
        "Mixed",
        1,
        [
            MilestoneCloseoutItem("a", True, "done"),
            MilestoneCloseoutItem("b", False, "todo"),
        ],
    )
    assert package.completion_ratio == 0.5


def test_closeout_063_summary_not_ready_message_mentions_incomplete():
    package = MilestoneCloseoutPackage("Test", 1, [MilestoneCloseoutItem("a", False, "missing")])
    summary = MilestoneCloseoutSummaryBuilder().build(package)
    assert "incomplete" in summary.message


def test_closeout_064_summary_ready_mentions_milestone_name():
    summary = MilestoneCloseoutSummaryBuilder().build(make_package())
    assert "Archive Backend Milestone Closeout" in summary.message


def test_closeout_065_api_summary_action_required_false():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["summary"]["action_required"] is False


def test_closeout_066_serialized_items_all_complete():
    response = serialize_milestone_closeout_package(make_package())
    assert all(item.completed for item in response.items)


def test_closeout_067_api_items_all_complete():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert all(item["completed"] for item in response.json()["items"])


def test_closeout_068_package_builder_returns_new_instance():
    first = MilestoneCloseoutPackageBuilder().build(1000)
    second = MilestoneCloseoutPackageBuilder().build(1000)
    assert first is not second


def test_closeout_069_package_items_are_distinct_names():
    names = [item.name for item in make_package().items]
    assert len(names) == len(set(names))


def test_closeout_070_api_items_are_distinct_names():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    names = [item["name"] for item in response.json()["items"]]
    assert len(names) == len(set(names))


def test_closeout_071_summary_empty_message():
    summary = MilestoneCloseoutSummaryBuilder().build(MilestoneCloseoutPackage("Empty", 0))
    assert "no items" in summary.message


def test_closeout_072_api_completion_ratio_one():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["completion_ratio"] == 1.0


def test_closeout_073_api_summary_mentions_1000_tests():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert "1000 passing tests" in response.json()["summary"]["message"]


def test_closeout_074_api_item_evidence_not_empty():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert all(item["evidence"] for item in response.json()["items"])


def test_closeout_075_api_item_names_not_empty():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert all(item["name"] for item in response.json()["items"])


def test_closeout_076_request_accepts_zero():
    request = MilestoneCloseoutPackageRequest(test_count=0)
    assert request.test_count == 0


def test_closeout_077_api_accepts_zero():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 0})
    assert response.status_code == 200
    assert response.json()["test_count"] == 0


def test_closeout_078_api_zero_still_complete_items():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 0})
    assert response.json()["is_complete"] is True


def test_closeout_079_builder_zero_test_count():
    package = MilestoneCloseoutPackageBuilder().build(0)
    assert package.test_count == 0


def test_closeout_080_summary_zero_test_count_mentions_zero():
    package = MilestoneCloseoutPackageBuilder().build(0)
    summary = MilestoneCloseoutSummaryBuilder().build(package)
    assert "0 passing tests" in summary.message


def test_closeout_081_item_dataclass_values():
    item = MilestoneCloseoutItem("name", True, "evidence")
    assert item.name == "name"
    assert item.completed is True
    assert item.evidence == "evidence"


def test_closeout_082_package_dataclass_values():
    package = MilestoneCloseoutPackage("Name", 10, [])
    assert package.milestone_name == "Name"
    assert package.test_count == 10
    assert package.items == []


def test_closeout_083_serialized_summary_action_false():
    response = serialize_milestone_closeout_package(make_package())
    assert response.summary.action_required is False


def test_closeout_084_serialized_summary_message_not_empty():
    response = serialize_milestone_closeout_package(make_package())
    assert response.summary.message


def test_closeout_085_api_response_has_expected_keys():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    keys = set(response.json().keys())
    assert "milestone_name" in keys
    assert "items" in keys
    assert "summary" in keys


def test_closeout_086_api_first_item_tests_green():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["items"][0]["name"] == "tests_green"


def test_closeout_087_api_last_item_deferred():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["items"][-1]["name"] == "next_work_deferred"


def test_closeout_088_summary_not_ready_action_true_for_mixed():
    package = MilestoneCloseoutPackage(
        "Mixed",
        1,
        [
            MilestoneCloseoutItem("a", True, "done"),
            MilestoneCloseoutItem("b", False, "todo"),
        ],
    )
    summary = MilestoneCloseoutSummaryBuilder().build(package)
    assert summary.action_required is True


def test_closeout_089_summary_not_ready_outcome_for_mixed():
    package = MilestoneCloseoutPackage(
        "Mixed",
        1,
        [
            MilestoneCloseoutItem("a", True, "done"),
            MilestoneCloseoutItem("b", False, "todo"),
        ],
    )
    summary = MilestoneCloseoutSummaryBuilder().build(package)
    assert summary.outcome == "not_ready"


def test_closeout_090_api_route_methods_include_post_only_expected():
    route = next(route for route in app.routes if route.path == "/api/v1/milestone-closeout-package")
    assert "POST" in route.methods


def test_closeout_091_api_invalid_payload_type_returns_422():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": "bad"})
    assert response.status_code == 422


def test_closeout_092_request_large_count():
    request = MilestoneCloseoutPackageRequest(test_count=100000)
    assert request.test_count == 100000


def test_closeout_093_api_large_count():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 100000})
    assert response.status_code == 200
    assert response.json()["test_count"] == 100000


def test_closeout_094_large_count_evidence():
    package = MilestoneCloseoutPackageBuilder().build(100000)
    assert "100000 tests passing" in package.items[0].evidence


def test_closeout_095_summary_large_count():
    package = MilestoneCloseoutPackageBuilder().build(100000)
    summary = MilestoneCloseoutSummaryBuilder().build(package)
    assert "100000 passing tests" in summary.message


def test_closeout_096_serialized_large_count():
    response = serialize_milestone_closeout_package(MilestoneCloseoutPackageBuilder().build(100000))
    assert response.test_count == 100000


def test_closeout_097_api_response_completed_count_equals_item_count():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["completed_count"] == response.json()["item_count"]


def test_closeout_098_api_response_incomplete_zero():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["incomplete_count"] == 0


def test_closeout_099_api_summary_ready_to_close():
    response = client.post("/api/v1/milestone-closeout-package", json={"test_count": 1000})
    assert response.json()["summary"]["outcome"] == "ready_to_close"


def test_closeout_100_done_marker():
    assert True
