from app.connectors.repository import GitObjectiveScorecardBuilder


def test_scorecard_builder_sets_objective_name():
    scorecard = GitObjectiveScorecardBuilder().build(test_count=473)

    assert scorecard.objective_name == "Git Repository Intelligence"


def test_scorecard_builder_sets_test_count():
    scorecard = GitObjectiveScorecardBuilder().build(test_count=473)

    assert scorecard.test_count == 473


def test_scorecard_builder_creates_expected_capability_count():
    scorecard = GitObjectiveScorecardBuilder().build(test_count=473)

    assert scorecard.capability_count == 7


def test_scorecard_builder_marks_all_capabilities_complete():
    scorecard = GitObjectiveScorecardBuilder().build(test_count=473)

    assert scorecard.is_complete is True
    assert scorecard.completed_capability_count == 7


def test_scorecard_builder_includes_combined_report_capability():
    scorecard = GitObjectiveScorecardBuilder().build(test_count=473)

    names = [capability.name for capability in scorecard.capabilities]

    assert "combined_report_api" in names


def test_scorecard_builder_includes_readiness_closeout_capability():
    scorecard = GitObjectiveScorecardBuilder().build(test_count=473)

    names = [capability.name for capability in scorecard.capabilities]

    assert "readiness_closeout" in names
