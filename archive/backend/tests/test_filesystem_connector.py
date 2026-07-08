from pathlib import Path

from app.connectors.filesystem import FilesystemConnector


def test_filesystem_connector_discovers_files(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello")
    (tmp_path / "b.md").write_text("world")

    connector = FilesystemConnector(str(tmp_path))

    files = connector.discover()

    assert len(files) == 2
