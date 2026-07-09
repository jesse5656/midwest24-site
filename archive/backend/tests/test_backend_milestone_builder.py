from app.connectors.repository import BackendMilestoneScorecardBuilder


def test_backend_milestone_builder_sets_name():
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=721)

    assert scorecard.milestone_name == "Archive Backend Milestone"


def test_backend_milestone_builder_sets_test_count():
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=721)

    assert scorecard.test_count == 721


def test_backend_milestone_builder_tracks_expected_capabilities():
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=721)

    assert scorecard.capability_count == 7


def test_backend_milestone_builder_marks_complete():
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=721)

    assert scorecard.is_complete is True


def test_backend_milestone_builder_includes_repository_ingestion():
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=721)

    assert "repository_ingestion" in [capability.name for capability in scorecard.capabilities]


def test_backend_milestone_builder_includes_git_intelligence():
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=721)

    assert "git_intelligence" in [capability.name for capability in scorecard.capabilities]


def test_backend_milestone_builder_includes_code_intelligence():
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=721)

    assert "code_intelligence" in [capability.name for capability in scorecard.capabilities]


def test_backend_milestone_builder_includes_backend_health():
    scorecard = BackendMilestoneScorecardBuilder().build(test_count=721)

    assert "backend_health" in [capability.name for capability in scorecard.capabilities]
