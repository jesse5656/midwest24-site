from pathlib import Path

from app.connectors.repository import SourceOutlinePreviewBuilder


def test_source_outline_builder_reads_python_file(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("def run():\n    pass\n", encoding="utf-8")

    preview = SourceOutlinePreviewBuilder().build(repo)

    assert preview.file_count == 1
    assert preview.symbol_count == 1


def test_source_outline_builder_reads_javascript_file(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.js").write_text("function run() {}\n", encoding="utf-8")

    preview = SourceOutlinePreviewBuilder().build(repo)

    assert preview.file_count == 1
    assert preview.symbol_count == 1


def test_source_outline_builder_skips_markdown_file(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")

    preview = SourceOutlinePreviewBuilder().build(repo)

    assert preview.file_count == 0


def test_source_outline_builder_handles_file_without_symbols(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("x = 1\n", encoding="utf-8")

    preview = SourceOutlinePreviewBuilder().build(repo)

    assert preview.file_count == 1
    assert preview.symbol_count == 0


def test_source_outline_builder_handles_nested_file(tmp_path: Path):
    repo = tmp_path / "repo"
    nested = repo / "src"
    nested.mkdir(parents=True)
    (nested / "main.py").write_text("def run():\n    pass\n", encoding="utf-8")

    preview = SourceOutlinePreviewBuilder().build(repo)

    assert preview.files[0].path == "src/main.py"
