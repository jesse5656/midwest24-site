from tests.test_code_intelligence_report_models import make_report
from app.connectors.repository import CodeIntelligenceReadinessEvaluator


def test_code_intelligence_readiness_passes_ready_report():
    readiness = CodeIntelligenceReadinessEvaluator().evaluate(make_report())

    assert readiness.passed is True
    assert readiness.failed_count == 0


def test_code_intelligence_readiness_fails_without_inventory():
    readiness = CodeIntelligenceReadinessEvaluator().evaluate(make_report(has_inventory=False))

    assert readiness.passed is False
    assert "has_inventory" in [check.name for check in readiness.failed_checks]


def test_code_intelligence_readiness_fails_without_symbols():
    readiness = CodeIntelligenceReadinessEvaluator().evaluate(make_report(has_symbols=False))

    assert readiness.passed is False
    assert "has_symbols" in [check.name for check in readiness.failed_checks]


def test_code_intelligence_readiness_counts_passed_and_failed_checks():
    readiness = CodeIntelligenceReadinessEvaluator().evaluate(make_report(has_inventory=False))

    assert readiness.passed_count >= 0
    assert readiness.failed_count >= 1


def test_code_intelligence_readiness_messages_are_operator_readable():
    readiness = CodeIntelligenceReadinessEvaluator().evaluate(make_report())

    messages = [check.message for check in readiness.checks]

    assert "Repository inventory is available." in messages
    assert "Repository languages are available." in messages
    assert "Source symbols are available." in messages
