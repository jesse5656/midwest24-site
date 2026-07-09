from app.api.repository_health import serialize_repository_health_report
from app.connectors.repository import RepositoryHealthCheck, RepositoryHealthReport


def test_serialize_health_report_maps_counts():
    report = RepositoryHealthReport(
        name="Health",
        checks=[
            RepositoryHealthCheck("a", True, "ok"),
            RepositoryHealthCheck("b", False, "bad", "warning"),
        ],
    )

    response = serialize_repository_health_report(report)

    assert response.check_count == 2
    assert response.passed_count == 1
    assert response.failed_count == 1
    assert response.warning_count == 1


def test_serialize_health_report_maps_checks():
    report = RepositoryHealthReport(
        name="Health",
        checks=[RepositoryHealthCheck("a", True, "ok")],
    )

    response = serialize_repository_health_report(report)

    assert response.checks[0].name == "a"
    assert response.checks[0].passed is True


def test_serialize_health_report_maps_summary():
    report = RepositoryHealthReport(
        name="Health",
        checks=[RepositoryHealthCheck("a", True, "ok")],
    )

    response = serialize_repository_health_report(report)

    assert response.summary.outcome == "healthy"
