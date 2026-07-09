from tests.test_code_intelligence_report_models import make_report
from app.connectors.repository import CodeIntelligenceSummaryBuilder


def test_code_intelligence_summary_reports_no_inventory():
    summary = CodeIntelligenceSummaryBuilder().build(make_report(has_inventory=False))

    assert summary.outcome == "no_inventory"
    assert summary.action_required is False


def test_code_intelligence_summary_reports_inventory_without_symbols():
    summary = CodeIntelligenceSummaryBuilder().build(make_report(has_symbols=False))

    assert summary.outcome == "inventory_without_symbols"
    assert "inventoried 1 file" in summary.message


def test_code_intelligence_summary_reports_ready():
    summary = CodeIntelligenceSummaryBuilder().build(make_report())

    assert summary.outcome == "ready"
    assert summary.action_required is False


def test_code_intelligence_summary_ready_message_mentions_symbols():
    summary = CodeIntelligenceSummaryBuilder().build(make_report())

    assert "1 symbol" in summary.message
