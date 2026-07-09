from app.connectors.repository import BackendMilestoneCloseoutBuilder, BackendMilestoneScorecard, BackendMilestoneScorecardBuilder


def test_backend_milestone_closeout_ready_when_complete():
    closeout = BackendMilestoneCloseoutBuilder().build(
        BackendMilestoneScorecardBuilder().build(test_count=721)
    )

    assert closeout.status == "ready_to_close"
    assert closeout.can_close is True
    assert closeout.next_action == "Prepare session transition prompt."


def test_backend_milestone_closeout_not_ready_without_tests():
    closeout = BackendMilestoneCloseoutBuilder().build(
        BackendMilestoneScorecardBuilder().build(test_count=0)
    )

    assert closeout.status == "not_ready"
    assert closeout.can_close is False


def test_backend_milestone_closeout_not_ready_empty_scorecard():
    closeout = BackendMilestoneCloseoutBuilder().build(
        BackendMilestoneScorecard("Archive Backend Milestone", 721)
    )

    assert closeout.status == "not_ready"
    assert closeout.can_close is False


def test_backend_milestone_closeout_preserves_milestone_name():
    closeout = BackendMilestoneCloseoutBuilder().build(
        BackendMilestoneScorecardBuilder().build(test_count=721)
    )

    assert closeout.milestone_name == "Archive Backend Milestone"
