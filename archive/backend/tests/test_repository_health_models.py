from app.connectors.repository import RepositoryHealthCheck, RepositoryHealthReport


def test_health_report_passes_when_all_checks_pass():
    report = RepositoryHealthReport(
        name="Health",
        checks=[
            RepositoryHealthCheck("a", True, "ok"),
            RepositoryHealthCheck("b", True, "ok"),
        ],
    )

    assert report.passed is True


def test_health_report_fails_when_any_check_fails():
    report = RepositoryHealthReport(
        name="Health",
        checks=[
            RepositoryHealthCheck("a", True, "ok"),
            RepositoryHealthCheck("b", False, "bad"),
        ],
    )

    assert report.passed is False


def test_health_report_counts_checks():
    report = RepositoryHealthReport(
        name="Health",
        checks=[
            RepositoryHealthCheck("a", True, "ok"),
            RepositoryHealthCheck("b", False, "bad"),
        ],
    )

    assert report.check_count == 2
    assert report.passed_count == 1
    assert report.failed_count == 1


def test_health_report_returns_failed_checks():
    failed = RepositoryHealthCheck("b", False, "bad")
    report = RepositoryHealthReport(
        name="Health",
        checks=[
            RepositoryHealthCheck("a", True, "ok"),
            failed,
        ],
    )

    assert report.failed_checks == [failed]


def test_health_report_counts_warnings_and_errors():
    report = RepositoryHealthReport(
        name="Health",
        checks=[
            RepositoryHealthCheck("a", False, "warn", "warning"),
            RepositoryHealthCheck("b", False, "err", "error"),
        ],
    )

    assert report.warning_count == 1
    assert report.error_count == 1


def test_health_report_empty_passes_by_default():
    report = RepositoryHealthReport(name="Health")

    assert report.passed is True
    assert report.check_count == 0


def test_health_check_default_severity_is_info():
    check = RepositoryHealthCheck("a", True, "ok")

    assert check.severity == "info"


def test_health_report_preserves_name():
    report = RepositoryHealthReport(name="Archive Backend Health")

    assert report.name == "Archive Backend Health"
