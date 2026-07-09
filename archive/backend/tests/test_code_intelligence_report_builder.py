from app.connectors.repository import (
    CodeIntelligenceReportBuilder,
    CodeInventoryPreview,
    SourceOutlinePreview,
)


class FakeInventoryBuilder:
    def __init__(self):
        self.repository_path = None

    def build(self, repository_path):
        self.repository_path = repository_path
        return CodeInventoryPreview()


class FakeOutlineBuilder:
    def __init__(self):
        self.repository_path = None

    def build(self, repository_path):
        self.repository_path = repository_path
        return SourceOutlinePreview()


def test_code_intelligence_report_builder_uses_inventory_builder():
    inventory_builder = FakeInventoryBuilder()
    outline_builder = FakeOutlineBuilder()

    CodeIntelligenceReportBuilder(
        inventory_builder=inventory_builder,
        outline_builder=outline_builder,
    ).build("/repo")

    assert inventory_builder.repository_path == "/repo"


def test_code_intelligence_report_builder_uses_outline_builder():
    inventory_builder = FakeInventoryBuilder()
    outline_builder = FakeOutlineBuilder()

    CodeIntelligenceReportBuilder(
        inventory_builder=inventory_builder,
        outline_builder=outline_builder,
    ).build("/repo")

    assert outline_builder.repository_path == "/repo"


def test_code_intelligence_report_builder_returns_report():
    report = CodeIntelligenceReportBuilder(
        inventory_builder=FakeInventoryBuilder(),
        outline_builder=FakeOutlineBuilder(),
    ).build("/repo")

    assert report.file_count == 0
    assert report.symbol_count == 0
