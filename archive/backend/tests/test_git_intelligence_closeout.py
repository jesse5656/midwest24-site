from tests.test_git_intelligence_report_models import make_report
from app.connectors.repository import GitAuthorshipPreview, GitCommitPreview, GitIntelligenceCloseoutBuilder


def test_git_intelligence_closeout_ready_for_ready_report():
    closeout = GitIntelligenceCloseoutBuilder().build(make_report())

    assert closeout.status == "ready_to_close"
    assert closeout.can_close is True
    assert closeout.next_action == "Promote the next Priority Queue item."


def test_git_intelligence_closeout_not_ready_for_non_repository():
    closeout = GitIntelligenceCloseoutBuilder().build(make_report(is_repository=False))

    assert closeout.status == "not_ready"
    assert closeout.can_close is False


def test_git_intelligence_closeout_not_ready_without_commits():
    closeout = GitIntelligenceCloseoutBuilder().build(
        make_report(commits=GitCommitPreview(), authorship=GitAuthorshipPreview())
    )

    assert closeout.status == "not_ready"
    assert closeout.can_close is False


def test_git_intelligence_closeout_preserves_custom_objective_name():
    closeout = GitIntelligenceCloseoutBuilder().build(
        make_report(),
        objective_name="Custom Git Objective",
    )

    assert closeout.objective_name == "Custom Git Objective"
