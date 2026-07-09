from fastapi.testclient import TestClient

from app.connectors.repository.operator_execution_rule import (
    OperatorExecutionPrompt,
    OperatorExecutionRuleBuilder,
)
from app.connectors.repository.operator_execution_summary import OperatorExecutionSummaryBuilder
from app.main import app

client = TestClient(app)


def test_operator_execution_rule_renders_ideal_prompt():
    prompt = OperatorExecutionRuleBuilder().build_prompt(825, 900)

    assert prompt.delta == 75
    assert prompt.is_forward_progress is True
    assert "825 passed" in prompt.render()
    assert "Go to 900" in prompt.render()
    assert "Python file writers" in prompt.render()
    assert "Avoid nested heredocs" in prompt.render()


def test_operator_execution_rule_summary_ready():
    ruleset = OperatorExecutionRuleBuilder().build_ruleset()
    summary = OperatorExecutionSummaryBuilder().build_for_ruleset(ruleset)

    assert summary.outcome == "ready"
    assert summary.action_required is False


def test_operator_execution_prompt_summary_invalid_target():
    rule = OperatorExecutionRuleBuilder().build_rule()
    prompt = OperatorExecutionPrompt(900, 825, rule)
    summary = OperatorExecutionSummaryBuilder().build_for_prompt(prompt)

    assert summary.outcome == "invalid_target"
    assert summary.action_required is True


def test_operator_execution_api_returns_prompt():
    response = client.post(
        "/api/v1/operator-execution-rule",
        json={"test_count": 825, "target_test_count": 900},
    )

    assert response.status_code == 200
    assert response.json()["prompt"]["delta"] == 75
    assert response.json()["prompt_summary"]["outcome"] == "ready"


def test_operator_execution_route_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/operator-execution-rule" in paths
