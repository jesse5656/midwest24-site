from pathlib import Path

from app.connectors.repository import RepositoryFilesystemConnector


def test_repository_discovery_report_counts_supported_unsupported_and_skipped_paths(tmp_path: Path):
    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")
    (repo / "image.png").write_bytes(b"skip")

    git_dir = repo / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\n", encoding="utf-8")

    node_modules = repo / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.json").write_text("{}", encoding="utf-8")

    report = RepositoryFilesystemConnector(repo).discover_with_report()

    assert report.supported_count == 1
    assert report.unsupported_count == 1
    assert report.skipped_count == 2

    assert report.supported_files[0].relative_path == "README.md"
    assert report.unsupported_files[0].path == "image.png"
    assert report.unsupported_files[0].suffix == ".png"

    skipped = {item.path: item.reason for item in report.skipped_paths}
    assert skipped[".git"] == "excluded_directory:.git"
    assert skipped["node_modules"] == "excluded_directory:node_modules"


def test_repository_discovery_report_preserves_legacy_discover_behavior(tmp_path: Path):
    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")
    (repo / "image.png").write_bytes(b"skip")

    files = RepositoryFilesystemConnector(repo).discover()

    assert len(files) == 1
    assert files[0].relative_path == "README.md"
