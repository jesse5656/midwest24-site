from app.connectors.repository import (
    CodeIntelligenceReport,
    CodeInventoryFile,
    CodeInventoryPreview,
    SourceOutlineFile,
    SourceOutlinePreview,
    SourceOutlineSymbol,
)


def make_report(has_inventory=True, has_symbols=True):
    inventory = CodeInventoryPreview(
        files=[CodeInventoryFile("main.py", ".py", "Python", 10)] if has_inventory else []
    )
    outline = SourceOutlinePreview(
        files=[
            SourceOutlineFile(
                "main.py",
                ".py",
                "Python",
                [SourceOutlineSymbol("run", "function", 1)] if has_symbols else [],
            )
        ] if has_inventory else []
    )
    return CodeIntelligenceReport(inventory=inventory, outline=outline)


def test_code_intelligence_report_counts_files():
    assert make_report().file_count == 1


def test_code_intelligence_report_counts_languages():
    assert make_report().language_count == 1


def test_code_intelligence_report_counts_symbols():
    assert make_report().symbol_count == 1


def test_code_intelligence_report_counts_functions():
    assert make_report().function_count == 1


def test_code_intelligence_report_counts_classes():
    report = CodeIntelligenceReport(
        inventory=CodeInventoryPreview(files=[CodeInventoryFile("main.py", ".py", "Python", 10)]),
        outline=SourceOutlinePreview(
            files=[
                SourceOutlineFile(
                    "main.py",
                    ".py",
                    "Python",
                    [SourceOutlineSymbol("Worker", "class", 1)],
                )
            ]
        ),
    )

    assert report.class_count == 1


def test_code_intelligence_report_counts_files_with_symbols():
    assert make_report().files_with_symbols_count == 1


def test_code_intelligence_report_has_inventory():
    assert make_report().has_inventory is True


def test_code_intelligence_report_has_no_inventory():
    assert make_report(has_inventory=False).has_inventory is False


def test_code_intelligence_report_has_outline():
    assert make_report().has_outline is True


def test_code_intelligence_report_has_no_outline_without_symbols():
    assert make_report(has_symbols=False).has_outline is False


def test_code_intelligence_report_ready_when_inventory_and_outline_exist():
    assert make_report().is_ready is True


def test_code_intelligence_report_not_ready_without_inventory():
    assert make_report(has_inventory=False).is_ready is False


def test_code_intelligence_report_not_ready_without_outline():
    assert make_report(has_symbols=False).is_ready is False
