from app.connectors.repository import (
    GitObjectiveCapability,
    GitObjectiveScorecard,
    GitObjectiveScorecardBuilder,
    GitObjectiveSummaryBuilder,
)


def test_objective_summary_reports_complete():
    scorecard = GitObjectiveScorecardBuilder().build(test_count=473)

    summary = GitObjectiveSummaryBuilder().build(scorecard)

    assert summary.outcome == "complete"
    assert summary.action_required is False
    assert "473 passing tests" in summary.message


def test_objective_summary_reports_not_started():
    summary = GitObjectiveSummaryBuilder().build(
        GitObjectiveScorecard(objective_name="Git Repository Intelligence")
    )

    assert summary.outcome == "not_started"
    assert summary.action_required is True


def test_objective_summary_reports_incomplete():
    scorecard = GitObjectiveScorecard(
        objective_name="Git Repository Intelligence",
        capabilities=[
            GitObjectiveCapability("a", True, "done"),
            GitObjectiveCapability("b", False, "todo"),
        ],
        test_count=473,
    )

    summary = GitObjectiveSummaryBuilder().build(scorecard)

    assert summary.outcome == "incomplete"
    assert summary.action_required is True


def test_objective_summary_complete_message_mentions_capability_ratio():
    scorecard = GitObjectiveScorecardBuilder().build(test_count=473)

    summary = GitObjectiveSummaryBuilder().build(scorecard)

    assert "7/7 capabilities" in summary.message


def test_objective_summary_incomplete_message_mentions_capability_ratio():
    scorecard = GitObjectiveScorecard(
        objective_name="Git Repository Intelligence",
        capabilities=[
            GitObjectiveCapability("a", True, "done"),
            GitObjectiveCapability("b", False, "todo"),
        ],
    )

    summary = GitObjectiveSummaryBuilder().build(scorecard)

    assert "1/2 capabilities" in summary.message
