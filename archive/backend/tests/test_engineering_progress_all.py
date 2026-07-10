from fastapi.testclient import TestClient

from app.api.engineering_progress import serialize_engineering_progress
from app.connectors.repository.engineering_progress import (
    EngineeringCapability,
    EngineeringProgress,
    EngineeringProgressBuilder,
)
from app.connectors.repository.engineering_progress_summary import EngineeringProgressSummaryBuilder
from app.main import app

client = TestClient(app)


def make_progress():
    return EngineeringProgressBuilder().build(test_count=3208)


def test_engineering_progress_001_capability_status_complete():
    capability = EngineeringCapability("Repository Structure", "complete")
    assert capability.is_complete is True


def test_engineering_progress_002_capability_status_in_progress():
    capability = EngineeringCapability("Knowledge Graph", "in_progress")
    assert capability.is_in_progress is True


def test_engineering_progress_003_capability_status_remaining():
    capability = EngineeringCapability("Semantic Code Search", "remaining")
    assert capability.is_remaining is True


def test_engineering_progress_004_milestone_name():
    assert make_progress().milestone_name == "Repository Intelligence Engine"


def test_engineering_progress_005_test_count():
    assert make_progress().test_count == 3208


def test_engineering_progress_006_capability_count():
    assert make_progress().capability_count == 11


def test_engineering_progress_007_complete_count():
    assert make_progress().complete_count == 6


def test_engineering_progress_008_in_progress_count():
    assert make_progress().in_progress_count == 1


def test_engineering_progress_009_remaining_count():
    assert make_progress().remaining_count == 4


def test_engineering_progress_010_percent_complete():
    assert make_progress().percent_complete == 0.5455


def test_engineering_progress_011_completed_capabilities():
    names = [capability.name for capability in make_progress().completed_capabilities]
    assert "Repository Structure" in names
    assert "Cross Reference Graph" in names


def test_engineering_progress_012_in_progress_capabilities():
    names = [capability.name for capability in make_progress().in_progress_capabilities]
    assert names == ["Knowledge Graph"]


def test_engineering_progress_013_remaining_capabilities():
    names = [capability.name for capability in make_progress().remaining_capabilities]
    assert "Semantic Code Search" in names
    assert "Drift Detection" in names


def test_engineering_progress_014_empty_percent_zero():
    progress = EngineeringProgress("Empty", 0, [])
    assert progress.percent_complete == 0.0


def test_engineering_progress_015_summary_in_progress():
    summary = EngineeringProgressSummaryBuilder().build(make_progress())
    assert summary.outcome == "in_progress"


def test_engineering_progress_016_summary_no_action():
    summary = EngineeringProgressSummaryBuilder().build(make_progress())
    assert summary.action_required is False


def test_engineering_progress_017_summary_mentions_percent():
    summary = EngineeringProgressSummaryBuilder().build(make_progress())
    assert "54% complete" in summary.message


def test_engineering_progress_018_summary_empty():
    summary = EngineeringProgressSummaryBuilder().build(EngineeringProgress("Empty", 0, []))
    assert summary.outcome == "no_capabilities"


def test_engineering_progress_019_summary_empty_requires_action():
    summary = EngineeringProgressSummaryBuilder().build(EngineeringProgress("Empty", 0, []))
    assert summary.action_required is True


def test_engineering_progress_020_summary_complete():
    progress = EngineeringProgress(
        "Complete",
        10,
        [EngineeringCapability("A", "complete"), EngineeringCapability("B", "complete")],
    )
    summary = EngineeringProgressSummaryBuilder().build(progress)
    assert summary.outcome == "complete"


def test_engineering_progress_021_serialize_counts():
    response = serialize_engineering_progress(make_progress())
    assert response.capability_count == 11
    assert response.complete_count == 6
    assert response.in_progress_count == 1
    assert response.remaining_count == 4


def test_engineering_progress_022_serialize_summary():
    response = serialize_engineering_progress(make_progress())
    assert response.summary.outcome == "in_progress"


def test_engineering_progress_023_serialize_completed():
    response = serialize_engineering_progress(make_progress())
    names = [capability.name for capability in response.completed_capabilities]
    assert "Repository Structure" in names


def test_engineering_progress_024_serialize_in_progress():
    response = serialize_engineering_progress(make_progress())
    names = [capability.name for capability in response.in_progress_capabilities]
    assert names == ["Knowledge Graph"]


def test_engineering_progress_025_serialize_remaining():
    response = serialize_engineering_progress(make_progress())
    names = [capability.name for capability in response.remaining_capabilities]
    assert "Architecture Report" in names


def test_engineering_progress_026_api_returns_200():
    response = client.post("/api/v1/engineering-progress", json={"test_count": 3208})
    assert response.status_code == 200


def test_engineering_progress_027_api_returns_milestone():
    response = client.post("/api/v1/engineering-progress", json={"test_count": 3208})
    assert response.json()["milestone_name"] == "Repository Intelligence Engine"


def test_engineering_progress_028_api_returns_test_count():
    response = client.post("/api/v1/engineering-progress", json={"test_count": 3208})
    assert response.json()["test_count"] == 3208


def test_engineering_progress_029_api_returns_counts():
    response = client.post("/api/v1/engineering-progress", json={"test_count": 3208})
    assert response.json()["capability_count"] == 11
    assert response.json()["complete_count"] == 6


def test_engineering_progress_030_api_returns_summary():
    response = client.post("/api/v1/engineering-progress", json={"test_count": 3208})
    assert response.json()["summary"]["outcome"] == "in_progress"


def test_engineering_progress_031_api_defaults_test_count():
    response = client.post("/api/v1/engineering-progress", json={})
    assert response.status_code == 200
    assert response.json()["test_count"] == 3208


def test_engineering_progress_032_api_rejects_negative_test_count():
    response = client.post("/api/v1/engineering-progress", json={"test_count": -1})
    assert response.status_code == 422


def test_engineering_progress_033_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/engineering-progress" in paths


def test_engineering_progress_034_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/engineering-progress")
    assert "POST" in route.methods


def test_engineering_progress_035_capability_evidence_preserved():
    capability = EngineeringCapability("A", "complete", "Evidence")
    assert capability.evidence == "Evidence"


def test_engineering_progress_036_builder_knowledge_graph_in_progress():
    capability = make_progress().in_progress_capabilities[0]
    assert capability.name == "Knowledge Graph"


def test_engineering_progress_037_builder_semantic_search_remaining():
    names = [capability.name for capability in make_progress().remaining_capabilities]
    assert "Semantic Code Search" in names


def test_engineering_progress_038_builder_architecture_report_remaining():
    names = [capability.name for capability in make_progress().remaining_capabilities]
    assert "Architecture Report" in names


def test_engineering_progress_039_builder_drift_detection_remaining():
    names = [capability.name for capability in make_progress().remaining_capabilities]
    assert "Drift Detection" in names


def test_engineering_progress_040_api_percent_complete():
    response = client.post("/api/v1/engineering-progress", json={"test_count": 3208})
    assert response.json()["percent_complete"] == 0.5455
