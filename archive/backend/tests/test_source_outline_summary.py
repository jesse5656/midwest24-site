from app.connectors.repository import (
    SourceOutlineFile,
    SourceOutlinePreview,
    SourceOutlineSummaryBuilder,
    SourceOutlineSymbol,
)


def test_source_outline_summary_reports_no_source_files():
    summary = SourceOutlineSummaryBuilder().build(SourceOutlinePreview())

    assert summary.outcome == "no_source_files"
    assert summary.action_required is False


def test_source_outline_summary_reports_no_symbols():
    preview = SourceOutlinePreview(
        files=[SourceOutlineFile("main.py", ".py", "Python", [])]
    )

    summary = SourceOutlineSummaryBuilder().build(preview)

    assert summary.outcome == "no_symbols"
    assert "1 file" in summary.message


def test_source_outline_summary_reports_symbols_found():
    preview = SourceOutlinePreview(
        files=[
            SourceOutlineFile(
                "main.py",
                ".py",
                "Python",
                [SourceOutlineSymbol("run", "function", 1)],
            )
        ]
    )

    summary = SourceOutlineSummaryBuilder().build(preview)

    assert summary.outcome == "symbols_found"
    assert "1 symbol" in summary.message


def test_source_outline_summary_mentions_files_with_symbols():
    preview = SourceOutlinePreview(
        files=[
            SourceOutlineFile(
                "a.py",
                ".py",
                "Python",
                [SourceOutlineSymbol("run", "function", 1)],
            ),
            SourceOutlineFile("b.py", ".py", "Python", []),
        ]
    )

    summary = SourceOutlineSummaryBuilder().build(preview)

    assert "1 file" in summary.message
