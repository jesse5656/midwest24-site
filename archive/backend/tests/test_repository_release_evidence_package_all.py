from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_release_evidence_package import (
    serialize_release_evidence_package,
)
from app.connectors.repository.repository_release_evidence_package import (
    RepositoryReleaseEvidencePackageBuilder,
    verify_release_evidence_package,
)
from app.connectors.repository.repository_release_evidence_package_summary import (
    RepositoryReleaseEvidencePackageSummaryBuilder,
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


def build_package(
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

    return RepositoryReleaseEvidencePackageBuilder().build(
        repository_path=candidate_repo,
        baseline=baseline,
        policy=RepositorySnapshotPolicy(
            require_fingerprint_match=True
        ),
    )


def test_package_001_accepted(tmp_path):
    package = build_package(tmp_path)
    assert package.accepted is True


def test_package_002_rejected(tmp_path):
    package = build_package(
        tmp_path,
        changed=True,
    )
    assert package.rejected is True


def test_package_003_evidence_count(tmp_path):
    package = build_package(tmp_path)
    assert package.evidence_count == 4


def test_package_004_component_names(tmp_path):
    package = build_package(tmp_path)
    assert package.component_names == [
        "certificate",
        "certificate_verification",
        "attestation",
        "attestation_verification",
    ]


def test_package_005_package_id_length(tmp_path):
    package = build_package(tmp_path)
    assert len(package.package_id) == 64


def test_package_006_package_valid(tmp_path):
    package = build_package(tmp_path)
    assert verify_release_evidence_package(package) is True


def test_package_007_status_accepted(tmp_path):
    package = build_package(tmp_path)
    assert package.status == "release_package_accepted"


def test_package_008_status_rejected(tmp_path):
    package = build_package(
        tmp_path,
        changed=True,
    )
    assert package.status == "release_package_rejected"


def test_package_009_failed_components(tmp_path):
    package = build_package(
        tmp_path,
        changed=True,
    )
    assert package.failed_component_count > 0


def test_package_010_summary_accepted(tmp_path):
    package = build_package(tmp_path)

    summary = (
        RepositoryReleaseEvidencePackageSummaryBuilder()
        .build(package)
    )

    assert summary.outcome == "release_package_accepted"


def test_package_011_summary_rejected(tmp_path):
    package = build_package(
        tmp_path,
        changed=True,
    )

    summary = (
        RepositoryReleaseEvidencePackageSummaryBuilder()
        .build(package)
    )

    assert summary.outcome == "release_package_rejected"


def test_package_012_serialize(tmp_path):
    package = build_package(tmp_path)

    response = serialize_release_evidence_package(
        package
    )

    assert response.accepted is True
    assert response.package_valid is True


def test_package_013_api_accepted(tmp_path):
    repo = make_repo(tmp_path / "repo")
    baseline = RepositorySnapshotBaselineBuilder().build(repo)

    response = client.post(
        "/api/v1/repository-release-evidence-package",
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
    assert response.json()["package_valid"] is True


def test_package_014_api_rejected(tmp_path):
    baseline_repo = make_repo(tmp_path / "baseline")
    candidate_repo = make_repo(
        tmp_path / "candidate",
        changed=True,
    )

    baseline = RepositorySnapshotBaselineBuilder().build(
        baseline_repo
    )

    response = client.post(
        "/api/v1/repository-release-evidence-package",
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


def test_package_015_api_invalid_baseline(tmp_path):
    repo = make_repo(tmp_path / "repo")

    response = client.post(
        "/api/v1/repository-release-evidence-package",
        json={
            "repository_path": str(repo),
            "baseline_json": "{invalid",
        },
    )

    assert response.status_code == 400


def test_package_016_api_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-release-evidence-package",
        json={
            "repository_path": str(tmp_path / "missing"),
            "baseline_json": "{}",
        },
    )

    assert response.status_code == 400


def test_package_017_route_registered():
    paths = {route.path for route in app.routes}

    assert (
        "/api/v1/repository-release-evidence-package"
        in paths
    )


def test_package_018_route_supports_post():
    route = next(
        route
        for route in app.routes
        if (
            route.path
            == "/api/v1/repository-release-evidence-package"
        )
    )

    assert "POST" in route.methods
