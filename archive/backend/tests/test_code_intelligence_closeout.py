from tests.test_code_intelligence_report_models import make_report
from app.connectors.repository import CodeIntelligenceCloseoutBuilder


def test_code_intelligence_closeout_ready_when_report_ready():
    closeout = CodeIntelligenceCloseoutBuilder().build(make_report())

    assert closeout.status == "ready_to_close"
    assert closeout.can_close is True


def test_code_intelligence_closeout_not_ready_without_inventory():
    closeout = CodeIntelligenceCloseoutBuilder().build(make_report(has_inventory=False))

    assert closeout.status == "not_ready"
    assert closeout.can_close is False


def test_code_intelligence_closeout_not_ready_without_symbols():
    closeout = CodeIntelligenceCloseoutBuilder().build(make_report(has_symbols=False))

    assert closeout.status == "not_ready"
    assert closeout.can_close is False


def test_code_intelligence_closeout_preserves_custom_objective_name():
    closeout = CodeIntelligenceCloseoutBuilder().build(
        make_report(),
        objective_name="Custom Code Objective",
    )

    assert closeout.objective_name == "Custom Code Objective"


def test_code_intelligence_closeout_next_action_ready():
    closeout = CodeIntelligenceCloseoutBuilder().build(make_report())

    assert closeout.next_action == "Promote the next Priority Queue item."
