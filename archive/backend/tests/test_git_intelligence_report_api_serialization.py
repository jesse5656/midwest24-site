from tests.test_git_intelligence_report_models import make_report
from app.api.git_intelligence_report import serialize_git_intelligence_report, serialize_git_intelligence_readiness
from app.connectors.repository import GitIntelligenceReadinessEvaluator


def test_serialize_git_intelligence_readiness_maps_counts():
    readiness = GitIntelligenceReadinessEvaluator().evaluate(make_report())

    response = serialize_git_intelligence_readiness(readiness)

    assert response.passed is True
    assert response.passed_count == len(readiness.checks)
    assert response.failed_count == 0


def test_serialize_git_intelligence_report_maps_top_level_counts():
    response = serialize_git_intelligence_report(make_report())

    assert response.is_repository is True
    assert response.commit_count == 1
    assert response.file_change_count == 1
    assert response.author_count == 1
    assert response.is_ready is True


def test_serialize_git_intelligence_report_maps_summary_and_closeout():
    response = serialize_git_intelligence_report(make_report())

    assert response.summary.outcome == "ready"
    assert response.closeout.status == "ready_to_close"
    assert response.closeout.can_close is True


def test_serialize_git_intelligence_report_maps_nested_sections():
    response = serialize_git_intelligence_report(make_report())

    assert response.repository.is_repository is True
    assert response.commits.commit_count == 1
    assert response.file_changes.file_change_count == 1
    assert response.authorship.author_count == 1
