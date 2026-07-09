from app.connectors.repository import (
    CodeInventoryFile,
    CodeInventoryLanguageSummary,
    CodeInventoryOperatorSummary,
    CodeInventoryPreview,
    CodeInventoryPreviewBuilder,
    CodeInventorySummaryBuilder,
    LANGUAGE_BY_SUFFIX,
)


def test_code_inventory_exports_are_available():
    assert CodeInventoryFile is not None
    assert CodeInventoryLanguageSummary is not None
    assert CodeInventoryPreview is not None
    assert CodeInventoryPreviewBuilder is not None


def test_code_inventory_summary_exports_are_available():
    assert CodeInventoryOperatorSummary is not None
    assert CodeInventorySummaryBuilder is not None


def test_language_by_suffix_export_contains_python():
    assert LANGUAGE_BY_SUFFIX[".py"] == "Python"
