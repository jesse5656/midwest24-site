from app.connectors.repository import SourceOutlineFile, SourceOutlinePreview, SourceOutlineSymbol


def test_source_outline_file_counts_symbols():
    file = SourceOutlineFile(
        path="main.py",
        suffix=".py",
        language="Python",
        symbols=[
            SourceOutlineSymbol("a", "function", 1),
            SourceOutlineSymbol("B", "class", 2),
        ],
    )

    assert file.symbol_count == 2
    assert file.function_count == 1
    assert file.class_count == 1


def test_source_outline_preview_counts_files_and_symbols():
    preview = SourceOutlinePreview(
        files=[
            SourceOutlineFile(
                "a.py",
                ".py",
                "Python",
                [SourceOutlineSymbol("a", "function", 1)],
            ),
            SourceOutlineFile(
                "b.py",
                ".py",
                "Python",
                [SourceOutlineSymbol("B", "class", 1)],
            ),
        ]
    )

    assert preview.file_count == 2
    assert preview.symbol_count == 2
    assert preview.function_count == 1
    assert preview.class_count == 1


def test_source_outline_preview_files_with_symbols():
    with_symbols = SourceOutlineFile(
        "a.py",
        ".py",
        "Python",
        [SourceOutlineSymbol("a", "function", 1)],
    )
    without_symbols = SourceOutlineFile("b.py", ".py", "Python", [])

    preview = SourceOutlinePreview(files=[with_symbols, without_symbols])

    assert preview.files_with_symbols == [with_symbols]


def test_source_outline_preview_empty_counts_zero():
    preview = SourceOutlinePreview()

    assert preview.file_count == 0
    assert preview.symbol_count == 0
    assert preview.function_count == 0
    assert preview.class_count == 0


def test_source_outline_symbol_preserves_line_number():
    symbol = SourceOutlineSymbol("run", "function", 42)

    assert symbol.line_number == 42
