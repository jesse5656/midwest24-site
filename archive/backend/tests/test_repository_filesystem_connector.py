from pathlib import Path

import pytest

from app.connectors.repository import RepositoryFilesystemConnector


def test_repository_filesystem_connector_discovers_supported_files(tmp_path: Path):
    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")
    (repo / "notes.txt").write_text("important notes\n", encoding="utf-8")
    (repo / "script.py").write_text("print('hello')\n", encoding="utf-8")
    (repo / "image.png").write_bytes(b"not supported")

    connector = RepositoryFilesystemConnector(repo)

    discovered = connector.discover()
    relative_paths = {item.relative_path for item in discovered}

    assert relative_paths == {
        "README.md",
        "notes.txt",
        "script.py",
    }


def test_repository_filesystem_connector_excludes_git_and_runtime_directories(tmp_path: Path):
    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")

    git_dir = repo / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\n", encoding="utf-8")

    node_modules = repo / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.json").write_text("{}", encoding="utf-8")

    pycache = repo / "__pycache__"
    pycache.mkdir()
    (pycache / "module.py").write_text("print('skip')\n", encoding="utf-8")

    connector = RepositoryFilesystemConnector(repo)

    discovered = connector.discover()
    relative_paths = {item.relative_path for item in discovered}

    assert relative_paths == {"README.md"}


def test_repository_filesystem_connector_returns_metadata(tmp_path: Path):
    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    file_path = repo / "OPERATING-PLAN.md"
    file_path.write_text("Execute the Operating Plan.\n", encoding="utf-8")

    connector = RepositoryFilesystemConnector(repo)

    discovered = connector.discover()

    assert len(discovered) == 1
    item = discovered[0]

    assert item.path == file_path.resolve()
    assert item.relative_path == "OPERATING-PLAN.md"
    assert item.suffix == ".md"
    assert item.size_bytes > 0


def test_repository_filesystem_connector_rejects_missing_path(tmp_path: Path):
    missing_path = tmp_path / "missing-repo"

    connector = RepositoryFilesystemConnector(missing_path)

    with pytest.raises(FileNotFoundError):
        connector.discover()


def test_repository_filesystem_connector_rejects_file_path(tmp_path: Path):
    file_path = tmp_path / "not-a-directory.md"
    file_path.write_text("not a repo\n", encoding="utf-8")

    connector = RepositoryFilesystemConnector(file_path)

    with pytest.raises(NotADirectoryError):
        connector.discover()
