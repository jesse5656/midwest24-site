from app.connectors.repository import SourceOutlineParser


def test_parser_detects_python_function():
    file = SourceOutlineParser().parse("main.py", ".py", "def run():\n    pass\n")

    assert file.symbols[0].name == "run"
    assert file.symbols[0].symbol_type == "function"
    assert file.symbols[0].line_number == 1


def test_parser_detects_python_class():
    file = SourceOutlineParser().parse("main.py", ".py", "class Worker:\n    pass\n")

    assert file.symbols[0].name == "Worker"
    assert file.symbols[0].symbol_type == "class"


def test_parser_detects_indented_python_method_as_function():
    file = SourceOutlineParser().parse(
        "main.py",
        ".py",
        "class Worker:\n    def run(self):\n        pass\n",
    )

    assert file.symbols[0].symbol_type == "class"
    assert file.symbols[1].name == "run"
    assert file.symbols[1].symbol_type == "function"
    assert file.symbols[1].line_number == 2


def test_parser_detects_javascript_function():
    file = SourceOutlineParser().parse("main.js", ".js", "function run() {}\n")

    assert file.symbols[0].name == "run"
    assert file.symbols[0].symbol_type == "function"


def test_parser_detects_exported_javascript_function():
    file = SourceOutlineParser().parse("main.js", ".js", "export function run() {}\n")

    assert file.symbols[0].name == "run"


def test_parser_detects_javascript_class():
    file = SourceOutlineParser().parse("main.js", ".js", "class Worker {}\n")

    assert file.symbols[0].name == "Worker"
    assert file.symbols[0].symbol_type == "class"


def test_parser_detects_exported_javascript_class():
    file = SourceOutlineParser().parse("main.js", ".js", "export class Worker {}\n")

    assert file.symbols[0].name == "Worker"


def test_parser_detects_const_arrow_function():
    file = SourceOutlineParser().parse("main.js", ".js", "const run = () => {}\n")

    assert file.symbols[0].name == "run"
    assert file.symbols[0].symbol_type == "function"


def test_parser_detects_typescript_arrow_function():
    file = SourceOutlineParser().parse("main.ts", ".ts", "export const run = async () => {}\n")

    assert file.symbols[0].name == "run"


def test_parser_ignores_markdown_symbols():
    file = SourceOutlineParser().parse("README.md", ".md", "# Title\n")

    assert file.symbols == []


def test_parser_sets_language_from_suffix():
    file = SourceOutlineParser().parse("main.py", ".py", "")

    assert file.language == "Python"


def test_parser_sets_unknown_language_for_unknown_suffix():
    file = SourceOutlineParser().parse("file.abc", ".abc", "")

    assert file.language == "Unknown"
