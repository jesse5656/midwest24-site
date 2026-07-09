from app.connectors.repository import GitObjectiveCapability, GitObjectiveScorecard


def test_scorecard_counts_capabilities():
    scorecard = GitObjectiveScorecard(
        objective_name="Git Repository Intelligence",
        capabilities=[
            GitObjectiveCapability("a", True, "done"),
            GitObjectiveCapability("b", False, "todo"),
        ],
        test_count=473,
    )

    assert scorecard.capability_count == 2
    assert scorecard.completed_capability_count == 1
    assert scorecard.incomplete_capability_count == 1


def test_scorecard_completion_ratio():
    scorecard = GitObjectiveScorecard(
        objective_name="Git Repository Intelligence",
        capabilities=[
            GitObjectiveCapability("a", True, "done"),
            GitObjectiveCapability("b", False, "todo"),
        ],
    )

    assert scorecard.completion_ratio == 0.5


def test_scorecard_completion_ratio_zero_without_capabilities():
    assert GitObjectiveScorecard("Git Repository Intelligence").completion_ratio == 0.0


def test_scorecard_complete_when_all_capabilities_complete():
    scorecard = GitObjectiveScorecard(
        objective_name="Git Repository Intelligence",
        capabilities=[GitObjectiveCapability("a", True, "done")],
    )

    assert scorecard.is_complete is True


def test_scorecard_not_complete_when_any_capability_incomplete():
    scorecard = GitObjectiveScorecard(
        objective_name="Git Repository Intelligence",
        capabilities=[
            GitObjectiveCapability("a", True, "done"),
            GitObjectiveCapability("b", False, "todo"),
        ],
    )

    assert scorecard.is_complete is False


def test_scorecard_not_complete_without_capabilities():
    assert GitObjectiveScorecard("Git Repository Intelligence").is_complete is False


def test_scorecard_preserves_test_count():
    scorecard = GitObjectiveScorecard(
        objective_name="Git Repository Intelligence",
        test_count=473,
    )

    assert scorecard.test_count == 473


def test_capability_preserves_evidence():
    capability = GitObjectiveCapability("api", True, "Endpoint exists.")

    assert capability.evidence == "Endpoint exists."
