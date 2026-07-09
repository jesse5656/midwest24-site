from app.connectors.repository import (
    BackendMilestoneCapability,
    BackendMilestoneReadinessEvaluator,
    BackendMilestoneScorecard,
    BackendMilestoneScorecardBuilder,
)


def test_backend_milestone_readiness_passes_complete_scorecard():
    readiness = BackendMilestoneReadinessEvaluator().evaluate(
        BackendMilestoneScorecardBuilder().build(test_count=721)
    )

    assert readiness.passed is True
    assert readiness.failed_count == 0


def test_backend_milestone_readiness_fails_without_tests():
    readiness = BackendMilestoneReadinessEvaluator().evaluate(
        BackendMilestoneScorecardBuilder().build(test_count=0)
    )

    assert readiness.passed is False
    assert "has_tests" in [check.name for check in readiness.failed_checks]


def test_backend_milestone_readiness_fails_incomplete_capabilities():
    scorecard = BackendMilestoneScorecard(
        milestone_name="Archive Backend Milestone",
        test_count=721,
        capabilities=[BackendMilestoneCapability("a", False, "todo")],
    )

    readiness = BackendMilestoneReadinessEvaluator().evaluate(scorecard)

    assert readiness.passed is False
    assert "all_capabilities_complete" in [check.name for check in readiness.failed_checks]


def test_backend_milestone_readiness_fails_low_capability_coverage():
    scorecard = BackendMilestoneScorecard(
        milestone_name="Archive Backend Milestone",
        test_count=721,
        capabilities=[BackendMilestoneCapability("a", True, "done")],
    )

    readiness = BackendMilestoneReadinessEvaluator().evaluate(scorecard)

    assert readiness.passed is False
    assert "capability_coverage" in [check.name for check in readiness.failed_checks]


def test_backend_milestone_readiness_counts_passed_and_failed():
    readiness = BackendMilestoneReadinessEvaluator().evaluate(
        BackendMilestoneScorecard("Archive Backend Milestone", 0)
    )

    assert readiness.failed_count >= 1
    assert readiness.passed_count >= 0
