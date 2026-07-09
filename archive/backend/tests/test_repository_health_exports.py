from app.connectors.repository import (
    ArchiveBackendHealthEvaluator,
    ArchiveBackendHealthInputs,
    RepositoryHealthCheck,
    RepositoryHealthOperatorSummary,
    RepositoryHealthReport,
    RepositoryHealthReportBuilder,
    RepositoryHealthSummaryBuilder,
)


def test_repository_health_exports_are_available():
    assert RepositoryHealthCheck is not None
    assert RepositoryHealthReport is not None
    assert RepositoryHealthReportBuilder is not None


def test_archive_backend_health_exports_are_available():
    assert ArchiveBackendHealthEvaluator is not None
    assert ArchiveBackendHealthInputs is not None


def test_repository_health_summary_exports_are_available():
    assert RepositoryHealthOperatorSummary is not None
    assert RepositoryHealthSummaryBuilder is not None
