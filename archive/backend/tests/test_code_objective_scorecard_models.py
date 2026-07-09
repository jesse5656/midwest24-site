from app.connectors.repository import CodeObjectiveCapability, CodeObjectiveScorecard


def test_code_scorecard_counts_capabilities():
    scorecard = CodeObjectiveScorecard(
        objective_name="Code Intelligence Preview",
        capabilities=[
            CodeObjectiveCapability("a", True, "done"),
            CodeObjectiveCapability("b", False, "todo"),
        ],
        test_count=645,
    )

    assert scorecard.capability_count == 2
    assert scorecard.completed_capability_count == 1
    assert scorecard.incomplete_capability_count == 1


def test_code_scorecard_completion_ratio():
    scorecard = CodeObjectiveScorecard(
        objective_name="Code Intelligence Preview",
        capabilities=[
            CodeObjectiveCapability("a", True, "done"),
            CodeObjectiveCapability("b", False, "todo"),
        ],
    )

    assert scorecard.completion_ratio == 0.5


def test_code_scorecard_completion_ratio_zero_without_capabilities():
    assert CodeObjectiveScorecard("Code Intelligence Preview").completion_ratio == 0.0


def test_code_scorecard_complete_when_all_capabilities_complete():
    scorecard = CodeObjectiveScorecard(
        objective_name="Code Intelligence Preview",
        capabilities=[CodeObjectiveCapability("a", True, "done")],
    )

    assert scorecard.is_complete is True


def test_code_scorecard_not_complete_when_any_capability_incomplete():
    scorecard = CodeObjectiveScorecard(
        objective_name="Code Intelligence Preview",
        capabilities=[
            CodeObjectiveCapability("a", True, "done"),
            CodeObjectiveCapability("b", False, "todo"),
        ],
    )

    assert scorecard.is_complete is False


def test_code_scorecard_not_complete_without_capabilities():
    assert CodeObjectiveScorecard("Code Intelligence Preview").is_complete is False


def test_code_scorecard_preserves_test_count():
    scorecard = CodeObjectiveScorecard(
        objective_name="Code Intelligence Preview",
        test_count=645,
    )

    assert scorecard.test_count == 645


def test_code_capability_preserves_evidence():
    capability = CodeObjectiveCapability("api", True, "Endpoint exists.")

    assert capability.evidence == "Endpoint exists."
