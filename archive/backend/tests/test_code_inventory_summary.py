from app.connectors.repository import CodeInventoryFile, CodeInventoryPreview, CodeInventorySummaryBuilder


def test_code_inventory_summary_reports_empty_inventory():
    summary = CodeInventorySummaryBuilder().build(CodeInventoryPreview())

    assert summary.outcome == "empty_inventory"
    assert summary.action_required is False


def test_code_inventory_summary_reports_single_language_inventory():
    preview = CodeInventoryPreview(
        files=[CodeInventoryFile("a.py", ".py", "Python", 10)]
    )

    summary = CodeInventorySummaryBuilder().build(preview)

    assert summary.outcome == "single_language_inventory"
    assert "one language" in summary.message


def test_code_inventory_summary_reports_multi_language_inventory():
    preview = CodeInventoryPreview(
        files=[
            CodeInventoryFile("a.py", ".py", "Python", 10),
            CodeInventoryFile("b.js", ".js", "JavaScript", 10),
        ]
    )

    summary = CodeInventorySummaryBuilder().build(preview)

    assert summary.outcome == "multi_language_inventory"
    assert "2 language" in summary.message


def test_code_inventory_summary_message_mentions_file_count():
    preview = CodeInventoryPreview(
        files=[
            CodeInventoryFile("a.py", ".py", "Python", 10),
            CodeInventoryFile("b.js", ".js", "JavaScript", 10),
        ]
    )

    summary = CodeInventorySummaryBuilder().build(preview)

    assert "2 file" in summary.message
