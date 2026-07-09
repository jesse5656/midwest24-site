from pathlib import Path

from app.connectors.repository import CodeInventoryPreviewBuilder


def test_code_inventory_builder_discovers_supported_files(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("print('hi')\n", encoding="utf-8")
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")

    preview = CodeInventoryPreviewBuilder().build(repo)

    assert preview.file_count == 2
    assert sorted(file.path for file in preview.files) == ["README.md", "main.py"]


def test_code_inventory_builder_maps_python_language(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("print('hi')\n", encoding="utf-8")

    preview = CodeInventoryPreviewBuilder().build(repo)

    assert preview.files[0].language == "Python"


def test_code_inventory_builder_maps_markdown_language(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")

    preview = CodeInventoryPreviewBuilder().build(repo)

    assert preview.files[0].language == "Markdown"


def test_code_inventory_builder_ignores_unsupported_files(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "image.png").write_bytes(b"skip")

    preview = CodeInventoryPreviewBuilder().build(repo)

    assert preview.file_count == 0


def test_code_inventory_builder_records_size(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    content = "hello\n"
    (repo / "README.md").write_text(content, encoding="utf-8")

    preview = CodeInventoryPreviewBuilder().build(repo)

    assert preview.files[0].size_bytes == len(content.encode("utf-8"))
