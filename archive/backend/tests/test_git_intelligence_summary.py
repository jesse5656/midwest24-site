from tests.test_git_intelligence_report_models import make_report
from app.connectors.repository import GitAuthorshipPreview, GitCommitPreview, GitIntelligenceSummaryBuilder


def test_git_intelligence_summary_reports_not_git_repository():
    summary = GitIntelligenceSummaryBuilder().build(make_report(is_repository=False))

    assert summary.outcome == "not_git_repository"
    assert summary.action_required is True


def test_git_intelligence_summary_reports_no_commits():
    report = make_report(commits=GitCommitPreview(), authorship=GitAuthorshipPreview())

    summary = GitIntelligenceSummaryBuilder().build(report)

    assert summary.outcome == "no_commits"
    assert summary.action_required is False


def test_git_intelligence_summary_reports_repository_has_changes():
    summary = GitIntelligenceSummaryBuilder().build(make_report(is_clean=False))

    assert summary.outcome == "repository_has_changes"
    assert summary.action_required is False
    assert "uncommitted changes" in summary.message


def test_git_intelligence_summary_reports_ready():
    summary = GitIntelligenceSummaryBuilder().build(make_report())

    assert summary.outcome == "ready"
    assert summary.action_required is False
    assert "Git repository intelligence is ready" in summary.message
