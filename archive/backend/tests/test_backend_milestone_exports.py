from app.connectors.repository import (
    BackendMilestoneCapability,
    BackendMilestoneCloseout,
    BackendMilestoneCloseoutBuilder,
    BackendMilestoneOperatorSummary,
    BackendMilestoneReadinessCheck,
    BackendMilestoneReadinessEvaluator,
    BackendMilestoneReadinessReport,
    BackendMilestoneScorecard,
    BackendMilestoneScorecardBuilder,
    BackendMilestoneSummaryBuilder,
)


def test_backend_milestone_scorecard_exports_are_available():
    assert BackendMilestoneCapability is not None
    assert BackendMilestoneScorecard is not None
    assert BackendMilestoneScorecardBuilder is not None


def test_backend_milestone_readiness_exports_are_available():
    assert BackendMilestoneReadinessCheck is not None
    assert BackendMilestoneReadinessReport is not None
    assert BackendMilestoneReadinessEvaluator is not None


def test_backend_milestone_closeout_exports_are_available():
    assert BackendMilestoneCloseout is not None
    assert BackendMilestoneCloseoutBuilder is not None
    assert BackendMilestoneOperatorSummary is not None
    assert BackendMilestoneSummaryBuilder is not None
