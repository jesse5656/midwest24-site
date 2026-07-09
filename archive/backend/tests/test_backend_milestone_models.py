from app.connectors.repository import BackendMilestoneCapability, BackendMilestoneScorecard


def test_backend_milestone_counts_capabilities():
    scorecard = BackendMilestoneScorecard(
        milestone_name="Archive Backend Milestone",
        test_count=721,
        capabilities=[
            BackendMilestoneCapability("a", True, "done"),
            BackendMilestoneCapability("b", False, "todo"),
        ],
    )

    assert scorecard.capability_count == 2
    assert scorecard.completed_capability_count == 1
    assert scorecard.incomplete_capability_count == 1


def test_backend_milestone_completion_ratio():
    scorecard = BackendMilestoneScorecard(
        milestone_name="Archive Backend Milestone",
        test_count=721,
        capabilities=[
            BackendMilestoneCapability("a", True, "done"),
            BackendMilestoneCapability("b", False, "todo"),
        ],
    )

    assert scorecard.completion_ratio == 0.5


def test_backend_milestone_completion_ratio_zero_without_capabilities():
    scorecard = BackendMilestoneScorecard("Archive Backend Milestone", 721)

    assert scorecard.completion_ratio == 0.0


def test_backend_milestone_complete_when_all_capabilities_complete():
    scorecard = BackendMilestoneScorecard(
        milestone_name="Archive Backend Milestone",
        test_count=721,
        capabilities=[BackendMilestoneCapability("a", True, "done")],
    )

    assert scorecard.is_complete is True


def test_backend_milestone_not_complete_with_incomplete_capability():
    scorecard = BackendMilestoneScorecard(
        milestone_name="Archive Backend Milestone",
        test_count=721,
        capabilities=[
            BackendMilestoneCapability("a", True, "done"),
            BackendMilestoneCapability("b", False, "todo"),
        ],
    )

    assert scorecard.is_complete is False


def test_backend_milestone_not_complete_without_capabilities():
    scorecard = BackendMilestoneScorecard("Archive Backend Milestone", 721)

    assert scorecard.is_complete is False


def test_backend_milestone_preserves_test_count():
    scorecard = BackendMilestoneScorecard("Archive Backend Milestone", 721)

    assert scorecard.test_count == 721


def test_backend_milestone_capability_preserves_evidence():
    capability = BackendMilestoneCapability("api", True, "Endpoint exists.")

    assert capability.evidence == "Endpoint exists."
