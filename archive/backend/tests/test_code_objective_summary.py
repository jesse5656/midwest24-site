from app.connectors.repository import (
    CodeObjectiveCapability,
    CodeObjectiveScorecard,
    CodeObjectiveScorecardBuilder,
    CodeObjectiveSummaryBuilder,
)


def test_code_objective_summary_reports_complete():
    scorecard = CodeObjectiveScorecardBuilder().build(test_count=645)

    summary = CodeObjectiveSummaryBuilder().build(scorecard)

    assert summary.outcome == "complete"
    assert summary.action_required is False
    assert "645 passing tests" in summary.message


def test_code_objective_summary_reports_not_started():
    summary = CodeObjectiveSummaryBuilder().build(
        CodeObjectiveScorecard(objective_name="Code Intelligence Preview")
    )

    assert summary.outcome == "not_started"
    assert summary.action_required is True


def test_code_objective_summary_reports_incomplete():
    scorecard = CodeObjectiveScorecard(
        objective_name="Code Intelligence Preview",
        capabilities=[
            CodeObjectiveCapability("a", True, "done"),
            CodeObjectiveCapability("b", False, "todo"),
        ],
        test_count=645,
    )

    summary = CodeObjectiveSummaryBuilder().build(scorecard)

    assert summary.outcome == "incomplete"
    assert summary.action_required is True


def test_code_objective_summary_complete_message_mentions_capability_ratio():
    scorecard = CodeObjectiveScorecardBuilder().build(test_count=645)

    summary = CodeObjectiveSummaryBuilder().build(scorecard)

    assert "5/5 capabilities" in summary.message


def test_code_objective_summary_incomplete_message_mentions_capability_ratio():
    scorecard = CodeObjectiveScorecard(
        objective_name="Code Intelligence Preview",
        capabilities=[
            CodeObjectiveCapability("a", True, "done"),
            CodeObjectiveCapability("b", False, "todo"),
        ],
    )

    summary = CodeObjectiveSummaryBuilder().build(scorecard)

    assert "1/2 capabilities" in summary.message
