from app.connectors.repository import CodeInventoryFile, CodeInventoryPreview


def test_code_inventory_preview_counts_files():
    preview = CodeInventoryPreview(
        files=[
            CodeInventoryFile("a.py", ".py", "Python", 10),
            CodeInventoryFile("b.js", ".js", "JavaScript", 20),
        ]
    )

    assert preview.file_count == 2


def test_code_inventory_preview_totals_size():
    preview = CodeInventoryPreview(
        files=[
            CodeInventoryFile("a.py", ".py", "Python", 10),
            CodeInventoryFile("b.js", ".js", "JavaScript", 20),
        ]
    )

    assert preview.total_size_bytes == 30


def test_code_inventory_preview_counts_languages():
    preview = CodeInventoryPreview(
        files=[
            CodeInventoryFile("a.py", ".py", "Python", 10),
            CodeInventoryFile("b.py", ".py", "Python", 20),
            CodeInventoryFile("c.js", ".js", "JavaScript", 30),
        ]
    )

    assert preview.language_count == 2


def test_code_inventory_preview_lists_languages_sorted():
    preview = CodeInventoryPreview(
        files=[
            CodeInventoryFile("b.js", ".js", "JavaScript", 20),
            CodeInventoryFile("a.py", ".py", "Python", 10),
        ]
    )

    assert preview.languages == ["JavaScript", "Python"]


def test_code_inventory_preview_largest_file():
    preview = CodeInventoryPreview(
        files=[
            CodeInventoryFile("small.py", ".py", "Python", 10),
            CodeInventoryFile("large.py", ".py", "Python", 20),
        ]
    )

    assert preview.largest_file.path == "large.py"


def test_code_inventory_preview_largest_file_none_when_empty():
    assert CodeInventoryPreview().largest_file is None


def test_code_inventory_language_summaries_group_by_language():
    preview = CodeInventoryPreview(
        files=[
            CodeInventoryFile("a.py", ".py", "Python", 10),
            CodeInventoryFile("b.py", ".py", "Python", 20),
            CodeInventoryFile("c.js", ".js", "JavaScript", 30),
        ]
    )

    summaries = preview.language_summaries

    assert summaries[0].language == "Python"
    assert summaries[0].file_count == 2
    assert summaries[0].size_bytes == 30


def test_code_inventory_language_summaries_sort_by_count_then_language():
    preview = CodeInventoryPreview(
        files=[
            CodeInventoryFile("z.py", ".py", "Python", 10),
            CodeInventoryFile("a.js", ".js", "JavaScript", 10),
        ]
    )

    assert [item.language for item in preview.language_summaries] == ["JavaScript", "Python"]


def test_code_inventory_file_preserves_suffix():
    file = CodeInventoryFile("README.md", ".md", "Markdown", 5)

    assert file.suffix == ".md"


def test_code_inventory_empty_preview_has_zero_counts():
    preview = CodeInventoryPreview()

    assert preview.file_count == 0
    assert preview.total_size_bytes == 0
    assert preview.language_count == 0
