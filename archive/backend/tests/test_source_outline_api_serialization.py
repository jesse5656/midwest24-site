from app.api.source_outline import (
    serialize_source_outline_file,
    serialize_source_outline_preview,
    serialize_source_outline_symbol,
)
from app.connectors.repository import SourceOutlineFile, SourceOutlinePreview, SourceOutlineSymbol


def test_serialize_source_outline_symbol_maps_fields():
    response = serialize_source_outline_symbol(SourceOutlineSymbol("run", "function", 1))

    assert response.name == "run"
    assert response.symbol_type == "function"


def test_serialize_source_outline_file_maps_counts():
    response = serialize_source_outline_file(
        SourceOutlineFile(
            "main.py",
            ".py",
            "Python",
            [SourceOutlineSymbol("run", "function", 1)],
        )
    )

    assert response.symbol_count == 1
    assert response.function_count == 1
    assert response.class_count == 0


def test_serialize_source_outline_preview_maps_counts():
    response = serialize_source_outline_preview(
        SourceOutlinePreview(
            files=[
                SourceOutlineFile(
                    "main.py",
                    ".py",
                    "Python",
                    [SourceOutlineSymbol("run", "function", 1)],
                )
            ]
        )
    )

    assert response.file_count == 1
    assert response.symbol_count == 1
    assert response.files_with_symbols_count == 1


def test_serialize_source_outline_preview_maps_summary():
    response = serialize_source_outline_preview(SourceOutlinePreview())

    assert response.summary.outcome == "no_source_files"
