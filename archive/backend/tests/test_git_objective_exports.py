from app.connectors.repository import (
    GitObjectiveCapability,
    GitObjectiveOperatorSummary,
    GitObjectiveScorecard,
    GitObjectiveScorecardBuilder,
    GitObjectiveSummaryBuilder,
)


def test_git_objective_scorecard_exports_are_available():
    assert GitObjectiveCapability is not None
    assert GitObjectiveScorecard is not None
    assert GitObjectiveScorecardBuilder is not None


def test_git_objective_summary_exports_are_available():
    assert GitObjectiveOperatorSummary is not None
    assert GitObjectiveSummaryBuilder is not None
