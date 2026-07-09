from app.api.code_inventory import serialize_code_inventory_file, serialize_code_inventory_preview
from app.connectors.repository import CodeInventoryFile, CodeInventoryPreview


def test_serialize_code_inventory_file_returns_none_for_none():
    assert serialize_code_inventory_file(None) is None


def test_serialize_code_inventory_file_maps_fields():
    response = serialize_code_inventory_file(
        CodeInventoryFile("main.py", ".py", "Python", 10)
    )

    assert response.path == "main.py"
    assert response.language == "Python"


def test_serialize_code_inventory_preview_maps_counts():
    response = serialize_code_inventory_preview(
        CodeInventoryPreview(
            files=[
                CodeInventoryFile("main.py", ".py", "Python", 10),
                CodeInventoryFile("README.md", ".md", "Markdown", 5),
            ]
        )
    )

    assert response.file_count == 2
    assert response.total_size_bytes == 15
    assert response.language_count == 2


def test_serialize_code_inventory_preview_maps_largest_file():
    response = serialize_code_inventory_preview(
        CodeInventoryPreview(
            files=[
                CodeInventoryFile("small.py", ".py", "Python", 10),
                CodeInventoryFile("large.py", ".py", "Python", 20),
            ]
        )
    )

    assert response.largest_file.path == "large.py"


def test_serialize_code_inventory_preview_maps_summary():
    response = serialize_code_inventory_preview(CodeInventoryPreview())

    assert response.summary.outcome == "empty_inventory"
