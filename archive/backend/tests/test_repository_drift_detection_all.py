from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_drift_detection import (
    serialize_repository_drift_report,
)
from app.connectors.repository.repository_drift_detection import (
    RepositoryDriftDetector,
    RepositoryDriftFinding,
    RepositoryDriftReport,
)
from app.connectors.repository.repository_drift_detection_summary import (
    RepositoryDriftSummaryBuilder,
)
from app.main import app

client = TestClient(app)


def make_repo(
    root: Path,
    changed: bool = False,
) -> Path:
    root.mkdir()

    requirements = (
        "fastapi\nsqlalchemy\n"
        if changed
        else "fastapi\n"
    )
    root.joinpath("requirements.txt").write_text(
        requirements,
        encoding="utf-8",
    )

    source = (
        "import json\n"
        "class Service:\n"
        "    def execute(self):\n"
        "        return json.dumps({})\n"
        if changed
        else
        "import os\n"
        "class Worker:\n"
        "    def run(self):\n"
        "        return os.getcwd()\n"
    )

    root.joinpath("app.py").write_text(
        source,
        encoding="utf-8",
    )

    if changed:
        root.joinpath("new_module.py").write_text(
            "def added_function():\n"
            "    return True\n",
            encoding="utf-8",
        )

    return root


def test_drift_001_empty_report_has_no_drift():
    report = RepositoryDriftReport("/a", "/b")
    assert report.has_drift is False


def test_drift_002_finding_count():
    report = RepositoryDriftReport(
        "/a",
        "/b",
        [RepositoryDriftFinding("added_file", "info", "x", "Added")],
    )
    assert report.finding_count == 1


def test_drift_003_added_count():
    report = RepositoryDriftReport(
        "/a",
        "/b",
        [RepositoryDriftFinding("added_file", "info", "x", "Added")],
    )
    assert report.added_count == 1


def test_drift_004_removed_count():
    report = RepositoryDriftReport(
        "/a",
        "/b",
        [RepositoryDriftFinding("removed_file", "warning", "x", "Removed")],
    )
    assert report.removed_count == 1


def test_drift_005_warning_count():
    report = RepositoryDriftReport(
        "/a",
        "/b",
        [RepositoryDriftFinding("removed_file", "warning", "x", "Removed")],
    )
    assert report.warning_count == 1


def test_drift_006_critical_count():
    report = RepositoryDriftReport(
        "/a",
        "/b",
        [RepositoryDriftFinding("removed_symbol", "critical", "x", "Removed")],
    )
    assert report.critical_count == 1


def test_drift_007_finding_types():
    report = RepositoryDriftReport(
        "/a",
        "/b",
        [
            RepositoryDriftFinding("removed_file", "warning", "x", "Removed"),
            RepositoryDriftFinding("added_file", "info", "y", "Added"),
        ],
    )
    assert report.finding_types == ["added_file", "removed_file"]


def test_drift_008_findings_by_type():
    report = RepositoryDriftReport(
        "/a",
        "/b",
        [RepositoryDriftFinding("added_file", "info", "x", "Added")],
    )
    assert len(report.findings_by_type("added_file")) == 1


def test_drift_009_identical_repositories(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(tmp_path / "candidate")

    report = RepositoryDriftDetector().compare(
        baseline,
        candidate,
    )

    assert report.has_drift is False


def test_drift_010_changed_repositories(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    report = RepositoryDriftDetector().compare(
        baseline,
        candidate,
    )

    assert report.has_drift is True


def test_drift_011_added_file(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    report = RepositoryDriftDetector().compare(
        baseline,
        candidate,
    )

    assert "added_file" in report.finding_types


def test_drift_012_removed_symbol(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    report = RepositoryDriftDetector().compare(
        baseline,
        candidate,
    )

    assert "removed_symbol" in report.finding_types


def test_drift_013_added_dependency(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    report = RepositoryDriftDetector().compare(
        baseline,
        candidate,
    )

    assert "added_dependency" in report.finding_types


def test_drift_014_removed_import(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    report = RepositoryDriftDetector().compare(
        baseline,
        candidate,
    )

    assert "removed_import" in report.finding_types


def test_drift_015_relationship_drift(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    report = RepositoryDriftDetector().compare(
        baseline,
        candidate,
    )

    assert any(
        finding.finding_type in {
            "added_relationship",
            "removed_relationship",
        }
        for finding in report.findings
    )


def test_drift_016_missing_baseline(tmp_path):
    candidate = make_repo(tmp_path / "candidate")

    try:
        RepositoryDriftDetector().compare(
            tmp_path / "missing",
            candidate,
        )
        assert False
    except FileNotFoundError:
        assert True


def test_drift_017_missing_candidate(tmp_path):
    baseline = make_repo(tmp_path / "baseline")

    try:
        RepositoryDriftDetector().compare(
            baseline,
            tmp_path / "missing",
        )
        assert False
    except FileNotFoundError:
        assert True


def test_drift_018_file_path(tmp_path):
    baseline = tmp_path / "baseline.py"
    baseline.write_text("x", encoding="utf-8")
    candidate = make_repo(tmp_path / "candidate")

    try:
        RepositoryDriftDetector().compare(
            baseline,
            candidate,
        )
        assert False
    except NotADirectoryError:
        assert True


def test_drift_019_summary_no_drift():
    summary = RepositoryDriftSummaryBuilder().build(
        RepositoryDriftReport("/a", "/b")
    )
    assert summary.outcome == "no_drift"


def test_drift_020_summary_warning():
    summary = RepositoryDriftSummaryBuilder().build(
        RepositoryDriftReport(
            "/a",
            "/b",
            [
                RepositoryDriftFinding(
                    "removed_file",
                    "warning",
                    "x",
                    "Removed",
                )
            ],
        )
    )
    assert summary.outcome == "drift_detected"


def test_drift_021_summary_critical():
    summary = RepositoryDriftSummaryBuilder().build(
        RepositoryDriftReport(
            "/a",
            "/b",
            [
                RepositoryDriftFinding(
                    "removed_symbol",
                    "critical",
                    "x",
                    "Removed",
                )
            ],
        )
    )
    assert summary.outcome == "critical_drift"


def test_drift_022_serialize():
    response = serialize_repository_drift_report(
        RepositoryDriftReport(
            "/a",
            "/b",
            [
                RepositoryDriftFinding(
                    "added_file",
                    "info",
                    "x",
                    "Added",
                )
            ],
        )
    )
    assert response.finding_count == 1
    assert response.has_drift is True


def test_drift_023_api_identical(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(tmp_path / "candidate")

    response = client.post(
        "/api/v1/repository-drift-detection",
        json={
            "baseline_repository_path": str(baseline),
            "candidate_repository_path": str(candidate),
        },
    )

    assert response.status_code == 200
    assert response.json()["has_drift"] is False


def test_drift_024_api_changed(tmp_path):
    baseline = make_repo(tmp_path / "baseline")
    candidate = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    response = client.post(
        "/api/v1/repository-drift-detection",
        json={
            "baseline_repository_path": str(baseline),
            "candidate_repository_path": str(candidate),
        },
    )

    assert response.status_code == 200
    assert response.json()["has_drift"] is True


def test_drift_025_api_missing_path(tmp_path):
    candidate = make_repo(tmp_path / "candidate")

    response = client.post(
        "/api/v1/repository-drift-detection",
        json={
            "baseline_repository_path": str(tmp_path / "missing"),
            "candidate_repository_path": str(candidate),
        },
    )

    assert response.status_code == 400


def test_drift_026_api_empty_path():
    response = client.post(
        "/api/v1/repository-drift-detection",
        json={
            "baseline_repository_path": "",
            "candidate_repository_path": "",
        },
    )

    assert response.status_code == 422


def test_drift_027_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-drift-detection" in paths


def test_drift_028_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path == "/api/v1/repository-drift-detection"
    )
    assert "POST" in route.methods
