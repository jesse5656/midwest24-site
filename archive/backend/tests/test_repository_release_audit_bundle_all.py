from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_audit_bundle import (
    serialize_repository_release_audit_bundle,
)
from app.connectors.repository.repository_release_audit_bundle import (
    RepositoryReleaseAuditBundleBuilder,
    verify_release_audit_bundle,
)
from app.connectors.repository.repository_release_audit_bundle_summary import (
    RepositoryReleaseAuditBundleSummaryBuilder,
)
from app.connectors.repository.repository_snapshot_baseline import (
    RepositorySnapshotBaselineBuilder,
)
from app.connectors.repository.repository_snapshot_policy import (
    RepositorySnapshotPolicy,
)
from app.main import app

client = TestClient(app)


def make_repo(
    root: Path,
    changed: bool = False,
) -> Path:
    root.mkdir()

    root.joinpath("requirements.txt").write_text(
        (
            "fastapi\npytest\nsqlalchemy\n"
            if changed
            else "fastapi\npytest\n"
        ),
        encoding="utf-8",
    )

    root.joinpath("app.py").write_text(
        (
            "import os\n"
            "import json\n"
            "class Worker:\n"
            "    def run(self):\n"
            "        return json.dumps({})\n"
            if changed
            else
            "import os\n"
            "class Worker:\n"
            "    def run(self):\n"
            "        return os.getcwd()\n"
        ),
        encoding="utf-8",
    )

    if changed:
        root.joinpath("extra.py").write_text(
            "def extra_function():\n"
            "    return True\n",
            encoding="utf-8",
        )

    return root


def build_bundle(
    tmp_path: Path,
    changed: bool = False,
):
    baseline_repo = make_repo(tmp_path / "baseline")

    candidate_repo = (
        make_repo(
            tmp_path / "candidate",
            changed=True,
        )
        if changed
        else baseline_repo
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    return RepositoryReleaseAuditBundleBuilder().build(
        repository_path=str(candidate_repo),
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )


def test_bundle_001_accepted(tmp_path):
    assert build_bundle(tmp_path).accepted is True


def test_bundle_002_rejected(tmp_path):
    assert build_bundle(
        tmp_path,
        changed=True,
    ).rejected is True


def test_bundle_003_exit_code_passed(tmp_path):
    assert build_bundle(tmp_path).exit_code == 0


def test_bundle_004_exit_code_failed(tmp_path):
    assert build_bundle(
        tmp_path,
        changed=True,
    ).exit_code == 1


def test_bundle_005_bundle_id(tmp_path):
    assert len(build_bundle(tmp_path).bundle_id) == 64


def test_bundle_006_bundle_valid(tmp_path):
    bundle = build_bundle(tmp_path)

    assert verify_release_audit_bundle(bundle) is True


def test_bundle_007_component_names(tmp_path):
    assert build_bundle(tmp_path).component_names == [
        "evidence_package",
        "evidence_package_verification",
        "audit_report",
        "audit_report_verification",
    ]


def test_bundle_008_failed_components(tmp_path):
    assert build_bundle(
        tmp_path,
        changed=True,
    ).failed_component_count > 0


def test_bundle_009_json(tmp_path):
    bundle = build_bundle(tmp_path)

    assert '"bundle_id"' in bundle.as_json()
    assert '"accepted": true' in bundle.as_json()


def test_bundle_010_markdown(tmp_path):
    markdown = build_bundle(tmp_path).as_markdown()

    assert "# Repository Release Audit Bundle" in markdown
    assert "**Accepted:** Yes" in markdown


def test_bundle_011_summary_accepted(tmp_path):
    summary = RepositoryReleaseAuditBundleSummaryBuilder().build(
        build_bundle(tmp_path)
    )

    assert summary.outcome == (
        "release_audit_bundle_accepted"
    )


def test_bundle_012_summary_rejected(tmp_path):
    summary = RepositoryReleaseAuditBundleSummaryBuilder().build(
        build_bundle(tmp_path, changed=True)
    )

    assert summary.outcome == (
        "release_audit_bundle_rejected"
    )


def test_bundle_013_serialize(tmp_path):
    response = serialize_repository_release_audit_bundle(
        build_bundle(tmp_path)
    )

    assert response.accepted is True
    assert response.bundle_valid is True


def test_bundle_014_api_accepted(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    response = client.post(
        "/api/v1/repository-release-audit-bundle",
        json={
            "repository_path": str(repo),
            "baseline_json": baseline.to_json(),
            "policy": {
                "require_fingerprint_match": True
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["bundle_valid"] is True


def test_bundle_015_api_rejected(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    response = client.post(
        "/api/v1/repository-release-audit-bundle",
        json={
            "repository_path": str(candidate_repo),
            "baseline_json": baseline.to_json(),
            "policy": {
                "require_fingerprint_match": True
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["rejected"] is True


def test_bundle_016_api_invalid_baseline(tmp_path):
    repo = make_repo(tmp_path / "repo")

    response = client.post(
        "/api/v1/repository-release-audit-bundle",
        json={
            "repository_path": str(repo),
            "baseline_json": "{invalid",
        },
    )

    assert response.status_code == 400


def test_bundle_017_api_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-release-audit-bundle",
        json={
            "repository_path": str(tmp_path / "missing"),
            "baseline_json": "{}",
        },
    )

    assert response.status_code == 400


def test_bundle_018_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-audit-bundle"
        in paths
    )


def test_bundle_019_route_supports_post():
    route = next(
        route
        for route in app.routes
        if (
            route.path
            == "/api/v1/repository-release-audit-bundle"
        )
    )

    assert "POST" in route.methods
