import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.operator_session_guard import (
    serialize_operator_session_guard_report,
    serialize_operator_session_guard_rule,
)
from app.connectors.repository.operator_session_guard import (
    OperatorSessionGuardBuilder,
    OperatorSessionGuardReport,
    OperatorSessionGuardRule,
)
from app.connectors.repository.operator_session_guard_summary import OperatorSessionGuardSummaryBuilder
from app.main import app
from app.schemas.operator_session_guard import OperatorSessionGuardRequest

client = TestClient(app)


def make_report():
    return OperatorSessionGuardBuilder().build(880, 940)


def test_operator_session_guard_001_delta():
    assert make_report().delta == 60


def test_operator_session_guard_002_forward_progress():
    assert make_report().is_forward_progress is True


def test_operator_session_guard_003_rule_count():
    assert make_report().rule_count == 5


def test_operator_session_guard_004_passed_count():
    assert make_report().passed_count == 5


def test_operator_session_guard_005_failed_count():
    assert make_report().failed_count == 0


def test_operator_session_guard_006_passed():
    assert make_report().passed is True


def test_operator_session_guard_007_no_failed_rules():
    assert make_report().failed_rules == []


def test_operator_session_guard_008_has_forward_progress_rule():
    assert "forward_progress" in [rule.name for rule in make_report().rules]


def test_operator_session_guard_009_has_python_file_writers_rule():
    assert "python_file_writers" in [rule.name for rule in make_report().rules]


def test_operator_session_guard_010_has_no_nested_heredocs_rule():
    assert "no_nested_heredocs" in [rule.name for rule in make_report().rules]


def test_operator_session_guard_011_has_test_run_rule():
    assert "test_run_included" in [rule.name for rule in make_report().rules]


def test_operator_session_guard_012_has_commit_separate_rule():
    assert "commit_commands_separate" in [rule.name for rule in make_report().rules]


def test_operator_session_guard_013_invalid_target_not_forward():
    report = OperatorSessionGuardBuilder().build(940, 880)
    assert report.is_forward_progress is False


def test_operator_session_guard_014_invalid_target_fails():
    report = OperatorSessionGuardBuilder().build(940, 880)
    assert report.passed is False


def test_operator_session_guard_015_invalid_target_failed_count():
    report = OperatorSessionGuardBuilder().build(940, 880)
    assert report.failed_count == 1


def test_operator_session_guard_016_invalid_target_failed_rule_name():
    report = OperatorSessionGuardBuilder().build(940, 880)
    assert report.failed_rules[0].name == "forward_progress"


def test_operator_session_guard_017_missing_python_writers_fails():
    report = OperatorSessionGuardBuilder().build(880, 940, uses_python_file_writers=False)
    assert report.passed is False


def test_operator_session_guard_018_missing_python_writers_failed_rule():
    report = OperatorSessionGuardBuilder().build(880, 940, uses_python_file_writers=False)
    assert "python_file_writers" in [rule.name for rule in report.failed_rules]


def test_operator_session_guard_019_nested_heredocs_fails():
    report = OperatorSessionGuardBuilder().build(880, 940, avoids_nested_heredocs=False)
    assert report.passed is False


def test_operator_session_guard_020_nested_heredocs_failed_rule():
    report = OperatorSessionGuardBuilder().build(880, 940, avoids_nested_heredocs=False)
    assert "no_nested_heredocs" in [rule.name for rule in report.failed_rules]


def test_operator_session_guard_021_missing_test_run_fails():
    report = OperatorSessionGuardBuilder().build(880, 940, includes_test_run=False)
    assert report.passed is False


def test_operator_session_guard_022_missing_test_run_failed_rule():
    report = OperatorSessionGuardBuilder().build(880, 940, includes_test_run=False)
    assert "test_run_included" in [rule.name for rule in report.failed_rules]


def test_operator_session_guard_023_commit_not_separate_fails():
    report = OperatorSessionGuardBuilder().build(880, 940, separates_commit_commands=False)
    assert report.passed is False


def test_operator_session_guard_024_commit_not_separate_failed_rule():
    report = OperatorSessionGuardBuilder().build(880, 940, separates_commit_commands=False)
    assert "commit_commands_separate" in [rule.name for rule in report.failed_rules]


def test_operator_session_guard_025_multiple_failures_count():
    report = OperatorSessionGuardBuilder().build(
        940,
        880,
        uses_python_file_writers=False,
        avoids_nested_heredocs=False,
        includes_test_run=False,
        separates_commit_commands=False,
    )
    assert report.failed_count == 5


def test_operator_session_guard_026_rule_message_preserved():
    rule = OperatorSessionGuardRule("a", True, "message")
    assert rule.message == "message"


def test_operator_session_guard_027_empty_report_not_passed():
    report = OperatorSessionGuardReport(880, 940, [])
    assert report.passed is False


def test_operator_session_guard_028_empty_report_rule_count_zero():
    report = OperatorSessionGuardReport(880, 940, [])
    assert report.rule_count == 0


def test_operator_session_guard_029_empty_report_failed_count_zero():
    report = OperatorSessionGuardReport(880, 940, [])
    assert report.failed_count == 0


def test_operator_session_guard_030_empty_report_passed_count_zero():
    report = OperatorSessionGuardReport(880, 940, [])
    assert report.passed_count == 0


def test_operator_session_guard_031_summary_ready():
    summary = OperatorSessionGuardSummaryBuilder().build(make_report())
    assert summary.outcome == "ready"


def test_operator_session_guard_032_summary_ready_no_action():
    summary = OperatorSessionGuardSummaryBuilder().build(make_report())
    assert summary.action_required is False


def test_operator_session_guard_033_summary_ready_mentions_delta():
    summary = OperatorSessionGuardSummaryBuilder().build(make_report())
    assert "60 additional" in summary.message


def test_operator_session_guard_034_summary_no_rules():
    summary = OperatorSessionGuardSummaryBuilder().build(OperatorSessionGuardReport(880, 940, []))
    assert summary.outcome == "no_rules"


def test_operator_session_guard_035_summary_no_rules_requires_action():
    summary = OperatorSessionGuardSummaryBuilder().build(OperatorSessionGuardReport(880, 940, []))
    assert summary.action_required is True


def test_operator_session_guard_036_summary_blocked():
    report = OperatorSessionGuardBuilder().build(940, 880)
    summary = OperatorSessionGuardSummaryBuilder().build(report)
    assert summary.outcome == "blocked"


def test_operator_session_guard_037_summary_blocked_requires_action():
    report = OperatorSessionGuardBuilder().build(940, 880)
    summary = OperatorSessionGuardSummaryBuilder().build(report)
    assert summary.action_required is True


def test_operator_session_guard_038_summary_blocked_mentions_failed_count():
    report = OperatorSessionGuardBuilder().build(940, 880)
    summary = OperatorSessionGuardSummaryBuilder().build(report)
    assert "failed 1/5" in summary.message


def test_operator_session_guard_039_request_defaults_true():
    request = OperatorSessionGuardRequest(current_test_count=880, target_test_count=940)
    assert request.uses_python_file_writers is True
    assert request.avoids_nested_heredocs is True
    assert request.includes_test_run is True
    assert request.separates_commit_commands is True


def test_operator_session_guard_040_request_rejects_negative_current():
    with pytest.raises(ValidationError):
        OperatorSessionGuardRequest(current_test_count=-1, target_test_count=940)


def test_operator_session_guard_041_request_rejects_negative_target():
    with pytest.raises(ValidationError):
        OperatorSessionGuardRequest(current_test_count=880, target_test_count=-1)


def test_operator_session_guard_042_serialize_rule_name():
    response = serialize_operator_session_guard_rule(OperatorSessionGuardRule("a", True, "ok"))
    assert response.name == "a"


def test_operator_session_guard_043_serialize_rule_passed():
    response = serialize_operator_session_guard_rule(OperatorSessionGuardRule("a", True, "ok"))
    assert response.passed is True


def test_operator_session_guard_044_serialize_report_counts():
    response = serialize_operator_session_guard_report(make_report())
    assert response.rule_count == 5
    assert response.passed_count == 5
    assert response.failed_count == 0


def test_operator_session_guard_045_serialize_report_delta():
    response = serialize_operator_session_guard_report(make_report())
    assert response.delta == 60


def test_operator_session_guard_046_serialize_report_summary():
    response = serialize_operator_session_guard_report(make_report())
    assert response.summary.outcome == "ready"


def test_operator_session_guard_047_serialize_report_failed_rules():
    report = OperatorSessionGuardBuilder().build(940, 880)
    response = serialize_operator_session_guard_report(report)
    assert response.failed_rules[0].name == "forward_progress"


def test_operator_session_guard_048_api_returns_200():
    response = client.post(
        "/api/v1/operator-session-guard",
        json={"current_test_count": 880, "target_test_count": 940},
    )
    assert response.status_code == 200


def test_operator_session_guard_049_api_returns_delta():
    response = client.post(
        "/api/v1/operator-session-guard",
        json={"current_test_count": 880, "target_test_count": 940},
    )
    assert response.json()["delta"] == 60


def test_operator_session_guard_050_api_returns_passed():
    response = client.post(
        "/api/v1/operator-session-guard",
        json={"current_test_count": 880, "target_test_count": 940},
    )
    assert response.json()["passed"] is True


def test_operator_session_guard_051_api_returns_ready_summary():
    response = client.post(
        "/api/v1/operator-session-guard",
        json={"current_test_count": 880, "target_test_count": 940},
    )
    assert response.json()["summary"]["outcome"] == "ready"


def test_operator_session_guard_052_api_invalid_target_blocked():
    response = client.post(
        "/api/v1/operator-session-guard",
        json={"current_test_count": 940, "target_test_count": 880},
    )
    assert response.json()["summary"]["outcome"] == "blocked"


def test_operator_session_guard_053_api_python_writer_false_blocks():
    response = client.post(
        "/api/v1/operator-session-guard",
        json={
            "current_test_count": 880,
            "target_test_count": 940,
            "uses_python_file_writers": False,
        },
    )
    assert response.json()["passed"] is False


def test_operator_session_guard_054_api_nested_heredoc_false_blocks():
    response = client.post(
        "/api/v1/operator-session-guard",
        json={
            "current_test_count": 880,
            "target_test_count": 940,
            "avoids_nested_heredocs": False,
        },
    )
    assert response.json()["passed"] is False


def test_operator_session_guard_055_api_test_run_false_blocks():
    response = client.post(
        "/api/v1/operator-session-guard",
        json={
            "current_test_count": 880,
            "target_test_count": 940,
            "includes_test_run": False,
        },
    )
    assert response.json()["passed"] is False


def test_operator_session_guard_056_api_commit_separate_false_blocks():
    response = client.post(
        "/api/v1/operator-session-guard",
        json={
            "current_test_count": 880,
            "target_test_count": 940,
            "separates_commit_commands": False,
        },
    )
    assert response.json()["passed"] is False


def test_operator_session_guard_057_api_rejects_negative_current():
    response = client.post(
        "/api/v1/operator-session-guard",
        json={"current_test_count": -1, "target_test_count": 940},
    )
    assert response.status_code == 422


def test_operator_session_guard_058_api_rejects_missing_target():
    response = client.post(
        "/api/v1/operator-session-guard",
        json={"current_test_count": 880},
    )
    assert response.status_code == 422


def test_operator_session_guard_059_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/operator-session-guard" in paths


def test_operator_session_guard_060_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/operator-session-guard")
    assert "POST" in route.methods
