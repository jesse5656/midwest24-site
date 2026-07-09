from tests.test_git_intelligence_report_models import make_report
from app.connectors.repository import GitAuthorshipPreview, GitCommitPreview, GitIntelligenceReadinessEvaluator


def test_git_intelligence_readiness_passes_ready_report():
    readiness = GitIntelligenceReadinessEvaluator().evaluate(make_report())

    assert readiness.passed is True
    assert readiness.failed_count == 0


def test_git_intelligence_readiness_fails_non_repository():
    readiness = GitIntelligenceReadinessEvaluator().evaluate(make_report(is_repository=False))

    assert readiness.passed is False
    assert "is_git_repository" in [check.name for check in readiness.failed_checks]


def test_git_intelligence_readiness_fails_without_commits():
    readiness = GitIntelligenceReadinessEvaluator().evaluate(
        make_report(commits=GitCommitPreview(), authorship=GitAuthorshipPreview())
    )

    assert readiness.passed is False
    assert "has_commits" in [check.name for check in readiness.failed_checks]
    assert "has_authorship" in [check.name for check in readiness.failed_checks]


def test_git_intelligence_readiness_counts_passed_and_failed_checks():
    readiness = GitIntelligenceReadinessEvaluator().evaluate(make_report(is_repository=False))

    assert readiness.passed_count >= 1
    assert readiness.failed_count >= 1


def test_git_intelligence_readiness_file_change_check_always_available():
    readiness = GitIntelligenceReadinessEvaluator().evaluate(make_report())

    assert "file_change_preview_available" in [check.name for check in readiness.checks]
