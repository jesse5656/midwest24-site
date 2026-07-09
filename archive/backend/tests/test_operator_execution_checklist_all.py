from fastapi.testclient import TestClient

from app.api.operator_execution_checklist import serialize_operator_execution_checklist
from app.connectors.repository.operator_execution_checklist import (
    OperatorExecutionChecklist,
    OperatorExecutionChecklistBuilder,
    OperatorExecutionChecklistItem,
)
from app.connectors.repository.operator_execution_checklist_summary import (
    OperatorExecutionChecklistSummaryBuilder,
)
from app.main import app

client = TestClient(app)


def make_checklist():
    return OperatorExecutionChecklistBuilder().build()


def test_operator_execution_checklist_001_name():
    assert make_checklist().name == "Copy/Paste Safe Execution Checklist"


def test_operator_execution_checklist_002_item_count():
    assert make_checklist().item_count == 5


def test_operator_execution_checklist_003_completed_count():
    assert make_checklist().completed_count == 5


def test_operator_execution_checklist_004_incomplete_count():
    assert make_checklist().incomplete_count == 0


def test_operator_execution_checklist_005_is_complete():
    assert make_checklist().is_complete is True


def test_operator_execution_checklist_006_has_single_bash_block():
    assert "single_bash_block" in [item.name for item in make_checklist().items]


def test_operator_execution_checklist_007_has_python_file_writers():
    assert "python_file_writers" in [item.name for item in make_checklist().items]


def test_operator_execution_checklist_008_has_no_nested_heredocs():
    assert "no_nested_heredocs" in [item.name for item in make_checklist().items]


def test_operator_execution_checklist_009_has_test_run_included():
    assert "test_run_included" in [item.name for item in make_checklist().items]


def test_operator_execution_checklist_010_has_commit_commands_separate():
    assert "commit_commands_separate" in [item.name for item in make_checklist().items]


def test_operator_execution_checklist_011_empty_not_complete():
    assert OperatorExecutionChecklist("Empty").is_complete is False


def test_operator_execution_checklist_012_empty_counts_zero():
    checklist = OperatorExecutionChecklist("Empty")
    assert checklist.item_count == 0
    assert checklist.completed_count == 0
    assert checklist.incomplete_count == 0


def test_operator_execution_checklist_013_incomplete_not_complete():
    checklist = OperatorExecutionChecklist(
        "Test",
        [OperatorExecutionChecklistItem("a", False, "missing")],
    )
    assert checklist.is_complete is False


def test_operator_execution_checklist_014_incomplete_count():
    checklist = OperatorExecutionChecklist(
        "Test",
        [
            OperatorExecutionChecklistItem("a", True, "done"),
            OperatorExecutionChecklistItem("b", False, "missing"),
        ],
    )
    assert checklist.incomplete_count == 1


def test_operator_execution_checklist_015_item_preserves_evidence():
    item = OperatorExecutionChecklistItem("a", True, "evidence")
    assert item.evidence == "evidence"


def test_operator_execution_checklist_016_summary_complete():
    summary = OperatorExecutionChecklistSummaryBuilder().build(make_checklist())
    assert summary.outcome == "complete"


def test_operator_execution_checklist_017_summary_complete_no_action():
    summary = OperatorExecutionChecklistSummaryBuilder().build(make_checklist())
    assert summary.action_required is False


def test_operator_execution_checklist_018_summary_empty():
    summary = OperatorExecutionChecklistSummaryBuilder().build(OperatorExecutionChecklist("Empty"))
    assert summary.outcome == "empty_checklist"


def test_operator_execution_checklist_019_summary_empty_requires_action():
    summary = OperatorExecutionChecklistSummaryBuilder().build(OperatorExecutionChecklist("Empty"))
    assert summary.action_required is True


def test_operator_execution_checklist_020_summary_incomplete():
    checklist = OperatorExecutionChecklist(
        "Test",
        [OperatorExecutionChecklistItem("a", False, "missing")],
    )
    summary = OperatorExecutionChecklistSummaryBuilder().build(checklist)
    assert summary.outcome == "incomplete"


def test_operator_execution_checklist_021_summary_incomplete_requires_action():
    checklist = OperatorExecutionChecklist(
        "Test",
        [OperatorExecutionChecklistItem("a", False, "missing")],
    )
    summary = OperatorExecutionChecklistSummaryBuilder().build(checklist)
    assert summary.action_required is True


def test_operator_execution_checklist_022_summary_message_mentions_ratio():
    summary = OperatorExecutionChecklistSummaryBuilder().build(make_checklist())
    assert "5/5" in summary.message


def test_operator_execution_checklist_023_serialize_name():
    response = serialize_operator_execution_checklist(make_checklist())
    assert response.name == "Copy/Paste Safe Execution Checklist"


def test_operator_execution_checklist_024_serialize_item_count():
    response = serialize_operator_execution_checklist(make_checklist())
    assert response.item_count == 5


def test_operator_execution_checklist_025_serialize_completed_count():
    response = serialize_operator_execution_checklist(make_checklist())
    assert response.completed_count == 5


def test_operator_execution_checklist_026_serialize_incomplete_count():
    response = serialize_operator_execution_checklist(make_checklist())
    assert response.incomplete_count == 0


def test_operator_execution_checklist_027_serialize_is_complete():
    response = serialize_operator_execution_checklist(make_checklist())
    assert response.is_complete is True


def test_operator_execution_checklist_028_serialize_items():
    response = serialize_operator_execution_checklist(make_checklist())
    assert response.items[0].name == "single_bash_block"


def test_operator_execution_checklist_029_serialize_summary():
    response = serialize_operator_execution_checklist(make_checklist())
    assert response.summary.outcome == "complete"


def test_operator_execution_checklist_030_api_returns_200():
    response = client.get("/api/v1/operator-execution-checklist")
    assert response.status_code == 200


def test_operator_execution_checklist_031_api_returns_name():
    response = client.get("/api/v1/operator-execution-checklist")
    assert response.json()["name"] == "Copy/Paste Safe Execution Checklist"


def test_operator_execution_checklist_032_api_returns_items():
    response = client.get("/api/v1/operator-execution-checklist")
    assert len(response.json()["items"]) == 5


def test_operator_execution_checklist_033_api_returns_complete():
    response = client.get("/api/v1/operator-execution-checklist")
    assert response.json()["is_complete"] is True


def test_operator_execution_checklist_034_api_returns_summary():
    response = client.get("/api/v1/operator-execution-checklist")
    assert response.json()["summary"]["outcome"] == "complete"


def test_operator_execution_checklist_035_api_contains_single_bash_block():
    response = client.get("/api/v1/operator-execution-checklist")
    names = [item["name"] for item in response.json()["items"]]
    assert "single_bash_block" in names


def test_operator_execution_checklist_036_api_contains_python_file_writers():
    response = client.get("/api/v1/operator-execution-checklist")
    names = [item["name"] for item in response.json()["items"]]
    assert "python_file_writers" in names


def test_operator_execution_checklist_037_api_contains_no_nested_heredocs():
    response = client.get("/api/v1/operator-execution-checklist")
    names = [item["name"] for item in response.json()["items"]]
    assert "no_nested_heredocs" in names


def test_operator_execution_checklist_038_api_contains_test_run():
    response = client.get("/api/v1/operator-execution-checklist")
    names = [item["name"] for item in response.json()["items"]]
    assert "test_run_included" in names


def test_operator_execution_checklist_039_api_contains_commit_separate():
    response = client.get("/api/v1/operator-execution-checklist")
    names = [item["name"] for item in response.json()["items"]]
    assert "commit_commands_separate" in names


def test_operator_execution_checklist_040_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/operator-execution-checklist" in paths


def test_operator_execution_checklist_041_route_supports_get():
    route = next(route for route in app.routes if route.path == "/api/v1/operator-execution-checklist")
    assert "GET" in route.methods


def test_operator_execution_checklist_042_all_default_items_completed():
    assert all(item.completed for item in make_checklist().items)


def test_operator_execution_checklist_043_all_default_items_have_evidence():
    assert all(item.evidence for item in make_checklist().items)


def test_operator_execution_checklist_044_builder_returns_new_instance():
    first = OperatorExecutionChecklistBuilder().build()
    second = OperatorExecutionChecklistBuilder().build()
    assert first is not second


def test_operator_execution_checklist_045_summary_ready_text():
    summary = OperatorExecutionChecklistSummaryBuilder().build(make_checklist())
    assert "complete" in summary.message


def test_operator_execution_checklist_046_api_evidence_mentions_python():
    response = client.get("/api/v1/operator-execution-checklist")
    evidence = " ".join(item["evidence"] for item in response.json()["items"])
    assert "Python" in evidence


def test_operator_execution_checklist_047_api_evidence_mentions_nested_heredocs():
    response = client.get("/api/v1/operator-execution-checklist")
    evidence = " ".join(item["evidence"] for item in response.json()["items"])
    assert "Nested heredocs" in evidence


def test_operator_execution_checklist_048_api_evidence_mentions_make_test():
    response = client.get("/api/v1/operator-execution-checklist")
    evidence = " ".join(item["evidence"] for item in response.json()["items"])
    assert "make test" in evidence


def test_operator_execution_checklist_049_api_evidence_mentions_commit():
    response = client.get("/api/v1/operator-execution-checklist")
    evidence = " ".join(item["evidence"] for item in response.json()["items"])
    assert "Commit commands" in evidence


def test_operator_execution_checklist_050_model_handles_mixed_items():
    checklist = OperatorExecutionChecklist(
        "Mixed",
        [
            OperatorExecutionChecklistItem("a", True, "done"),
            OperatorExecutionChecklistItem("b", False, "todo"),
            OperatorExecutionChecklistItem("c", True, "done"),
        ],
    )
    assert checklist.item_count == 3
    assert checklist.completed_count == 2
    assert checklist.incomplete_count == 1
    assert checklist.is_complete is False
