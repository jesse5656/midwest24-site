from tests.test_code_intelligence_report_models import make_report
from app.api.code_intelligence_report import (
    serialize_code_intelligence_readiness,
    serialize_code_intelligence_report,
)
from app.connectors.repository import CodeIntelligenceReadinessEvaluator


def test_serialize_code_intelligence_readiness_maps_counts():
    readiness = CodeIntelligenceReadinessEvaluator().evaluate(make_report())

    response = serialize_code_intelligence_readiness(readiness)

    assert response.passed is True
    assert response.failed_count == 0


def test_serialize_code_intelligence_report_maps_top_level_counts():
    response = serialize_code_intelligence_report(make_report())

    assert response.file_count == 1
    assert response.language_count == 1
    assert response.symbol_count == 1
    assert response.function_count == 1


def test_serialize_code_intelligence_report_maps_summary_and_closeout():
    response = serialize_code_intelligence_report(make_report())

    assert response.summary.outcome == "ready"
    assert response.closeout.status == "ready_to_close"


def test_serialize_code_intelligence_report_maps_nested_inventory_and_outline():
    response = serialize_code_intelligence_report(make_report())

    assert response.inventory.file_count == 1
    assert response.outline.symbol_count == 1


def test_serialize_code_intelligence_report_maps_not_ready():
    response = serialize_code_intelligence_report(make_report(has_symbols=False))

    assert response.is_ready is False
    assert response.closeout.can_close is False
