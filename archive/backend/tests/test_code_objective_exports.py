from app.connectors.repository import (
    CodeObjectiveCapability,
    CodeObjectiveOperatorSummary,
    CodeObjectiveScorecard,
    CodeObjectiveScorecardBuilder,
    CodeObjectiveSummaryBuilder,
)


def test_code_objective_scorecard_exports_are_available():
    assert CodeObjectiveCapability is not None
    assert CodeObjectiveScorecard is not None
    assert CodeObjectiveScorecardBuilder is not None


def test_code_objective_summary_exports_are_available():
    assert CodeObjectiveOperatorSummary is not None
    assert CodeObjectiveSummaryBuilder is not None
