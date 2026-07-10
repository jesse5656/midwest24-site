from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_symbol_index import serialize_repository_symbol_index
from app.connectors.repository.repository_symbol_index import (
    RepositorySymbol,
    RepositorySymbolIndex,
    RepositorySymbolIndexBuilder,
)
from app.connectors.repository.repository_symbol_index_summary import RepositorySymbolIndexSummaryBuilder
from app.main import app

client = TestClient(app)


def make_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app").mkdir()
    (repo / "app" / "main.py").write_text(
        "MAX_SIZE = 10\n"
        "class Worker:\n"
        "    def run(self):\n"
        "        return True\n"
        "async def fetch():\n"
        "    return None\n"
        "def helper():\n"
        "    return 1\n",
        encoding="utf-8",
    )
    (repo / "app" / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "ignored.py").write_text("class Ignored:\n    pass\n", encoding="utf-8")
    return repo


def test_symbol_index_001_qualified_name_without_parent():
    symbol = RepositorySymbol("helper", "function", "app/main.py", 1)
    assert symbol.qualified_name == "helper"


def test_symbol_index_002_qualified_name_with_parent():
    symbol = RepositorySymbol("run", "method", "app/main.py", 3, parent="Worker")
    assert symbol.qualified_name == "Worker.run"


def test_symbol_index_003_manual_symbol_count():
    index = RepositorySymbolIndex("/repo", [RepositorySymbol("A", "class", "a.py", 1)])
    assert index.symbol_count == 1


def test_symbol_index_004_manual_source_files():
    index = RepositorySymbolIndex("/repo", [RepositorySymbol("A", "class", "a.py", 1)])
    assert index.source_files == ["a.py"]


def test_symbol_index_005_manual_symbol_types():
    index = RepositorySymbolIndex(
        "/repo",
        [
            RepositorySymbol("A", "class", "a.py", 1),
            RepositorySymbol("b", "function", "a.py", 2),
        ],
    )
    assert index.symbol_types == ["class", "function"]


def test_symbol_index_006_class_count():
    index = RepositorySymbolIndex("/repo", [RepositorySymbol("A", "class", "a.py", 1)])
    assert index.class_count == 1


def test_symbol_index_007_function_count():
    index = RepositorySymbolIndex("/repo", [RepositorySymbol("a", "function", "a.py", 1)])
    assert index.function_count == 1


def test_symbol_index_008_method_count():
    index = RepositorySymbolIndex("/repo", [RepositorySymbol("a", "method", "a.py", 1)])
    assert index.method_count == 1


def test_symbol_index_009_constant_count():
    index = RepositorySymbolIndex("/repo", [RepositorySymbol("A", "constant", "a.py", 1)])
    assert index.constant_count == 1


def test_symbol_index_010_symbols_for_file():
    index = RepositorySymbolIndex(
        "/repo",
        [
            RepositorySymbol("A", "class", "a.py", 1),
            RepositorySymbol("B", "class", "b.py", 1),
        ],
    )
    assert [symbol.name for symbol in index.symbols_for_file("a.py")] == ["A"]


def test_symbol_index_011_symbols_by_type():
    index = RepositorySymbolIndex(
        "/repo",
        [
            RepositorySymbol("A", "class", "a.py", 1),
            RepositorySymbol("b", "function", "a.py", 2),
        ],
    )
    assert [symbol.name for symbol in index.symbols_by_type("class")] == ["A"]


def test_symbol_index_012_builder_finds_class(tmp_path):
    repo = make_repo(tmp_path)
    index = RepositorySymbolIndexBuilder().build(repo)
    assert "Worker" in [symbol.name for symbol in index.symbols]


def test_symbol_index_013_builder_finds_method(tmp_path):
    repo = make_repo(tmp_path)
    index = RepositorySymbolIndexBuilder().build(repo)
    assert "Worker.run" in [symbol.qualified_name for symbol in index.symbols]


def test_symbol_index_014_builder_finds_async_function(tmp_path):
    repo = make_repo(tmp_path)
    index = RepositorySymbolIndexBuilder().build(repo)
    assert "fetch" in [symbol.name for symbol in index.symbols]


def test_symbol_index_015_builder_finds_function(tmp_path):
    repo = make_repo(tmp_path)
    index = RepositorySymbolIndexBuilder().build(repo)
    assert "helper" in [symbol.name for symbol in index.symbols]


def test_symbol_index_016_builder_finds_constant(tmp_path):
    repo = make_repo(tmp_path)
    index = RepositorySymbolIndexBuilder().build(repo)
    assert "MAX_SIZE" in [symbol.name for symbol in index.symbols]


def test_symbol_index_017_builder_ignores_git(tmp_path):
    repo = make_repo(tmp_path)
    index = RepositorySymbolIndexBuilder().build(repo)
    assert "Ignored" not in [symbol.name for symbol in index.symbols]


def test_symbol_index_018_builder_ignores_syntax_errors(tmp_path):
    repo = make_repo(tmp_path)
    index = RepositorySymbolIndexBuilder().build(repo)
    assert "app/broken.py" not in index.source_files


def test_symbol_index_019_builder_symbol_count(tmp_path):
    repo = make_repo(tmp_path)
    index = RepositorySymbolIndexBuilder().build(repo)
    assert index.symbol_count == 5


def test_symbol_index_020_builder_source_file_count(tmp_path):
    repo = make_repo(tmp_path)
    index = RepositorySymbolIndexBuilder().build(repo)
    assert index.source_file_count == 1


def test_symbol_index_021_builder_type_counts(tmp_path):
    repo = make_repo(tmp_path)
    index = RepositorySymbolIndexBuilder().build(repo)
    assert index.class_count == 1
    assert index.method_count == 1
    assert index.function_count == 2
    assert index.constant_count == 1


def test_symbol_index_022_builder_respects_depth(tmp_path):
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "main.py").write_text("class Deep:\n    pass\n", encoding="utf-8")
    index = RepositorySymbolIndexBuilder().build(repo, max_depth=1)
    assert index.symbol_count == 0


def test_symbol_index_023_builder_missing_path_raises(tmp_path):
    try:
        RepositorySymbolIndexBuilder().build(tmp_path / "missing")
        assert False
    except FileNotFoundError:
        assert True


def test_symbol_index_024_builder_file_path_raises(tmp_path):
    path = tmp_path / "file.py"
    path.write_text("class A:\n    pass\n", encoding="utf-8")
    try:
        RepositorySymbolIndexBuilder().build(path)
        assert False
    except NotADirectoryError:
        assert True


def test_symbol_index_025_summary_no_symbols():
    summary = RepositorySymbolIndexSummaryBuilder().build(RepositorySymbolIndex("/repo"))
    assert summary.outcome == "no_symbols"


def test_symbol_index_026_summary_detected():
    index = RepositorySymbolIndex("/repo", [RepositorySymbol("A", "class", "a.py", 1)])
    summary = RepositorySymbolIndexSummaryBuilder().build(index)
    assert summary.outcome == "symbols_detected"


def test_symbol_index_027_summary_no_action():
    index = RepositorySymbolIndex("/repo", [RepositorySymbol("A", "class", "a.py", 1)])
    summary = RepositorySymbolIndexSummaryBuilder().build(index)
    assert summary.action_required is False


def test_symbol_index_028_summary_mentions_symbol_count():
    index = RepositorySymbolIndex("/repo", [RepositorySymbol("A", "class", "a.py", 1)])
    summary = RepositorySymbolIndexSummaryBuilder().build(index)
    assert "1 symbol" in summary.message


def test_symbol_index_029_serialize_counts():
    index = RepositorySymbolIndex("/repo", [RepositorySymbol("A", "class", "a.py", 1)])
    response = serialize_repository_symbol_index(index)
    assert response.symbol_count == 1
    assert response.class_count == 1


def test_symbol_index_030_serialize_summary():
    index = RepositorySymbolIndex("/repo", [RepositorySymbol("A", "class", "a.py", 1)])
    response = serialize_repository_symbol_index(index)
    assert response.summary.outcome == "symbols_detected"


def test_symbol_index_031_api_returns_200(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-symbol-index", json={"repository_path": str(repo)})
    assert response.status_code == 200


def test_symbol_index_032_api_returns_symbol_count(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-symbol-index", json={"repository_path": str(repo)})
    assert response.json()["symbol_count"] == 5


def test_symbol_index_033_api_returns_source_files(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-symbol-index", json={"repository_path": str(repo)})
    assert response.json()["source_files"] == ["app/main.py"]


def test_symbol_index_034_api_returns_symbol_types(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-symbol-index", json={"repository_path": str(repo)})
    assert response.json()["symbol_types"] == ["class", "constant", "function", "method"]


def test_symbol_index_035_api_returns_qualified_method(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post("/api/v1/repository-symbol-index", json={"repository_path": str(repo)})
    qualified = [symbol["qualified_name"] for symbol in response.json()["symbols"]]
    assert "Worker.run" in qualified


def test_symbol_index_036_api_respects_depth(tmp_path):
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "main.py").write_text("class Deep:\n    pass\n", encoding="utf-8")
    response = client.post(
        "/api/v1/repository-symbol-index",
        json={"repository_path": str(repo), "max_depth": 1},
    )
    assert response.json()["symbol_count"] == 0


def test_symbol_index_037_api_rejects_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-symbol-index",
        json={"repository_path": str(tmp_path / "missing")},
    )
    assert response.status_code == 400


def test_symbol_index_038_api_rejects_empty_path():
    response = client.post("/api/v1/repository-symbol-index", json={"repository_path": ""})
    assert response.status_code == 422


def test_symbol_index_039_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-symbol-index" in paths


def test_symbol_index_040_route_supports_post():
    route = next(route for route in app.routes if route.path == "/api/v1/repository-symbol-index")
    assert "POST" in route.methods
