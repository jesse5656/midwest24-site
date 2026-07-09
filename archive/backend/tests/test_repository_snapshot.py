from pathlib import Path

from app.connectors.repository import RepositorySnapshotter


def test_repository_snapshotter_captures_supported_files(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")
    (repo / "image.png").write_bytes(b"skip")

    snapshot = RepositorySnapshotter().snapshot(repo)

    assert snapshot.repository_path == str(repo.resolve())
    assert snapshot.paths() == {"README.md"}


def test_repository_snapshotter_records_size_suffix_and_fingerprint(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    content = "# Repo\n"
    (repo / "README.md").write_text(content, encoding="utf-8")

    snapshot = RepositorySnapshotter().snapshot(repo)
    entry = snapshot.get("README.md")

    assert entry.size_bytes == len(content.encode("utf-8"))
    assert entry.suffix == ".md"
    assert len(entry.fingerprint) == 64


def test_repository_snapshotter_ignores_excluded_directories(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")

    git_dir = repo / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\n", encoding="utf-8")

    snapshot = RepositorySnapshotter().snapshot(repo)

    assert snapshot.paths() == {"README.md"}
