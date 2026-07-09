from app.connectors.repository import (
    BackendMilestoneCapability,
    BackendMilestoneScorecard,
    BackendMilestoneScorecardBuilder,
    BackendMilestoneSummaryBuilder,
)


def test_backend_milestone_summary_reports_complete():
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=721)

    summary = BackendMilestoneSummaryBuilder().build(scorecard)

    assert summary.outcome == "complete"
    assert summary.action_required is False


def test_backend_milestone_summary_complete_message_mentions_tests():
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=721)

    summary = BackendMilestoneSummaryBuilder().build(scorecard)

    assert "721 passing tests" in summary.message


def test_backend_milestone_summary_reports_not_started():
    summary = BackendMilestoneSummaryBuilder().build(
        BackendMilestoneScorecard("Archive Backend Milestone", 0)
    )

    assert summary.outcome == "not_started"
    assert summary.action_required is True


def test_backend_milestone_summary_reports_incomplete():
    scorecard = BackendMilestoneScorecard(
        milestone_name="Archive Backend Milestone",
        test_count=721,
        capabilities=[
            BackendMilestoneCapability("a", True, "done"),
            BackendMilestoneCapability("b", False, "todo"),
        ],
    )

    summary = BackendMilestoneSummaryBuilder().build(scorecard)

    assert summary.outcome == "incomplete"
    assert summary.action_required is True


def test_backend_milestone_summary_complete_message_mentions_capability_ratio():
    summary = BackendMilestoneSummaryBuilder().build(
        BackendMilestoneScorecardBuilder().build(test_count=721)
    )

    assert "7/7 capabilities" in summary.message
