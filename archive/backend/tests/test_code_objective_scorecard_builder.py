from app.connectors.repository import CodeObjectiveScorecardBuilder


def test_code_scorecard_builder_sets_objective_name():
    scorecard = CodeObjectiveScorecardBuilder().build(test_count=645)

    assert scorecard.objective_name == "Code Intelligence Preview"


def test_code_scorecard_builder_sets_test_count():
    scorecard = CodeObjectiveScorecardBuilder().build(test_count=645)

    assert scorecard.test_count == 645


def test_code_scorecard_builder_creates_expected_capability_count():
    scorecard = CodeObjectiveScorecardBuilder().build(test_count=645)

    assert scorecard.capability_count == 5


def test_code_scorecard_builder_marks_all_capabilities_complete():
    scorecard = CodeObjectiveScorecardBuilder().build(test_count=645)

    assert scorecard.is_complete is True
    assert scorecard.completed_capability_count == 5


def test_code_scorecard_builder_includes_inventory_capability():
    scorecard = CodeObjectiveScorecardBuilder().build(test_count=645)

    names = [capability.name for capability in scorecard.capabilities]

    assert "code_inventory_api" in names


def test_code_scorecard_builder_includes_source_outline_capability():
    scorecard = CodeObjectiveScorecardBuilder().build(test_count=645)

    names = [capability.name for capability in scorecard.capabilities]

    assert "source_outline_api" in names


def test_code_scorecard_builder_includes_report_capability():
    scorecard = CodeObjectiveScorecardBuilder().build(test_count=645)

    names = [capability.name for capability in scorecard.capabilities]

    assert "code_intelligence_report_api" in names
