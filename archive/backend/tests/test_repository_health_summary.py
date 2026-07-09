from app.connectors.repository import (
    RepositoryHealthCheck,
    RepositoryHealthReport,
    RepositoryHealthSummaryBuilder,
)


def test_health_summary_reports_no_checks():
    summary = RepositoryHealthSummaryBuilder().build(RepositoryHealthReport(name="Health"))

    assert summary.outcome == "no_checks"
    assert summary.action_required is True


def test_health_summary_reports_healthy():
    report = RepositoryHealthReport(
        name="Health",
        checks=[RepositoryHealthCheck("a", True, "ok")],
    )

    summary = RepositoryHealthSummaryBuilder().build(report)

    assert summary.outcome == "healthy"
    assert summary.action_required is False


def test_health_summary_reports_unhealthy_when_errors_exist():
    report = RepositoryHealthReport(
        name="Health",
        checks=[RepositoryHealthCheck("a", False, "bad", "error")],
    )

    summary = RepositoryHealthSummaryBuilder().build(report)

    assert summary.outcome == "unhealthy"
    assert summary.action_required is True


def test_health_summary_reports_warnings_without_errors():
    report = RepositoryHealthReport(
        name="Health",
        checks=[RepositoryHealthCheck("a", False, "warn", "warning")],
    )

    summary = RepositoryHealthSummaryBuilder().build(report)

    assert summary.outcome == "warnings"
    assert summary.action_required is False


def test_health_summary_healthy_message_mentions_counts():
    report = RepositoryHealthReport(
        name="Health",
        checks=[
            RepositoryHealthCheck("a", True, "ok"),
            RepositoryHealthCheck("b", True, "ok"),
        ],
    )

    summary = RepositoryHealthSummaryBuilder().build(report)

    assert "2/2 health checks" in summary.message
