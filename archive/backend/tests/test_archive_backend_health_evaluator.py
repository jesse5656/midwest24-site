from app.connectors.repository import ArchiveBackendHealthEvaluator, ArchiveBackendHealthInputs


def make_inputs(**kwargs):
    defaults = {
        "test_count": 684,
        "has_progress_ledger": True,
        "has_operating_plan": True,
        "has_runbook": True,
        "has_git_intelligence": True,
        "has_code_intelligence": True,
    }
    defaults.update(kwargs)
    return ArchiveBackendHealthInputs(**defaults)


def test_archive_backend_health_passes_when_all_inputs_present():
    report = ArchiveBackendHealthEvaluator().evaluate(make_inputs())

    assert report.passed is True
    assert report.failed_count == 0


def test_archive_backend_health_fails_without_tests():
    report = ArchiveBackendHealthEvaluator().evaluate(make_inputs(test_count=0))

    assert report.passed is False
    assert "tests_present" in [check.name for check in report.failed_checks]


def test_archive_backend_health_fails_without_progress_ledger():
    report = ArchiveBackendHealthEvaluator().evaluate(make_inputs(has_progress_ledger=False))

    assert report.passed is False
    assert "progress_ledger_present" in [check.name for check in report.failed_checks]


def test_archive_backend_health_fails_without_operating_plan():
    report = ArchiveBackendHealthEvaluator().evaluate(make_inputs(has_operating_plan=False))

    assert report.passed is False
    assert "operating_plan_present" in [check.name for check in report.failed_checks]


def test_archive_backend_health_warns_without_runbook():
    report = ArchiveBackendHealthEvaluator().evaluate(make_inputs(has_runbook=False))

    assert report.passed is False
    failed = report.failed_checks[0]
    assert failed.name == "runbook_present"
    assert failed.severity == "warning"


def test_archive_backend_health_warns_without_git_intelligence():
    report = ArchiveBackendHealthEvaluator().evaluate(make_inputs(has_git_intelligence=False))

    assert report.passed is False
    assert "git_intelligence_present" in [check.name for check in report.failed_checks]


def test_archive_backend_health_warns_without_code_intelligence():
    report = ArchiveBackendHealthEvaluator().evaluate(make_inputs(has_code_intelligence=False))

    assert report.passed is False
    assert "code_intelligence_present" in [check.name for check in report.failed_checks]


def test_archive_backend_health_tests_message_includes_count():
    report = ArchiveBackendHealthEvaluator().evaluate(make_inputs(test_count=750))

    test_check = next(check for check in report.checks if check.name == "tests_present")

    assert "750 tests" in test_check.message
