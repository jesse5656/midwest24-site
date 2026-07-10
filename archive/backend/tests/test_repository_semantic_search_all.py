from pathlib import Path

from fastapi.testclient import TestClient

from app.api.repository_semantic_search import (
    serialize_repository_semantic_search_report,
)
from app.connectors.repository.repository_semantic_search import (
    RepositorySemanticSearchEngine,
    RepositorySemanticSearchReport,
    RepositorySemanticSearchResult,
    expand_query_tokens,
    normalize_tokens,
)
from app.connectors.repository.repository_semantic_search_summary import (
    RepositorySemanticSearchSummaryBuilder,
)
from app.main import app

client = TestClient(app)


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "requirements.txt").write_text(
        "fastapi\npytest\n",
        encoding="utf-8",
    )

    (repo / "app.py").write_text(
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "class WorkerService:\n"
        "    def search_repository(self):\n"
        "        return True\n",
        encoding="utf-8",
    )

    return repo


def test_semantic_search_001_normalize_tokens():
    assert normalize_tokens("WorkerService_search") == [
        "worker",
        "service",
        "search",
    ]


def test_semantic_search_002_expand_api_aliases():
    expanded = expand_query_tokens(["api"])
    assert "endpoint" in expanded
    assert "router" in expanded


def test_semantic_search_003_reverse_alias_expansion():
    expanded = expand_query_tokens(["endpoint"])
    assert "api" in expanded


def test_semantic_search_004_manual_result_count():
    report = RepositorySemanticSearchReport(
        "/repo",
        "worker",
        [
            RepositorySemanticSearchResult(
                "1",
                "symbol",
                "Worker",
                "app.py",
                3,
                0,
                3,
                ["worker"],
            )
        ],
    )
    assert report.result_count == 1


def test_semantic_search_005_manual_document_types():
    report = RepositorySemanticSearchReport(
        "/repo",
        "worker",
        [
            RepositorySemanticSearchResult(
                "1",
                "symbol",
                "Worker",
                "app.py",
                3,
                0,
                3,
                ["worker"],
            )
        ],
    )
    assert report.document_types == ["symbol"]


def test_semantic_search_006_manual_highest_score():
    report = RepositorySemanticSearchReport(
        "/repo",
        "worker",
        [
            RepositorySemanticSearchResult(
                "1",
                "symbol",
                "Worker",
                "app.py",
                3,
                0,
                5,
                ["worker"],
            ),
            RepositorySemanticSearchResult(
                "2",
                "file",
                "app.py",
                "app.py",
                3,
                0,
                3,
                ["worker"],
            ),
        ],
    )
    assert report.highest_score == 5


def test_semantic_search_007_empty_highest_score():
    report = RepositorySemanticSearchReport("/repo", "none", [])
    assert report.highest_score == 0


def test_semantic_search_008_engine_finds_worker(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositorySemanticSearchEngine().search(repo, "worker")
    assert report.result_count > 0


def test_semantic_search_009_engine_finds_repository_search(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositorySemanticSearchEngine().search(
        repo,
        "repository search",
    )
    assert report.result_count > 0


def test_semantic_search_010_engine_matches_api_concept(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositorySemanticSearchEngine().search(repo, "api")
    assert report.result_count > 0


def test_semantic_search_011_engine_matches_endpoint_alias(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositorySemanticSearchEngine().search(repo, "endpoint")
    assert report.result_count > 0


def test_semantic_search_012_engine_matches_dependency_concept(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositorySemanticSearchEngine().search(repo, "dependency")
    assert report.result_count > 0


def test_semantic_search_013_engine_respects_limit(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositorySemanticSearchEngine().search(
        repo,
        "app",
        limit=1,
    )
    assert report.result_count <= 1


def test_semantic_search_014_engine_empty_query(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositorySemanticSearchEngine().search(repo, " ")
    assert report.result_count == 0


def test_semantic_search_015_engine_missing_path(tmp_path):
    try:
        RepositorySemanticSearchEngine().search(
            tmp_path / "missing",
            "worker",
        )
        assert False
    except FileNotFoundError:
        assert True


def test_semantic_search_016_engine_file_path(tmp_path):
    file_path = tmp_path / "file.py"
    file_path.write_text("x", encoding="utf-8")

    try:
        RepositorySemanticSearchEngine().search(file_path, "worker")
        assert False
    except NotADirectoryError:
        assert True


def test_semantic_search_017_summary_empty_query():
    report = RepositorySemanticSearchReport("/repo", "", [])
    summary = RepositorySemanticSearchSummaryBuilder().build(report)
    assert summary.outcome == "empty_query"


def test_semantic_search_018_summary_no_results():
    report = RepositorySemanticSearchReport("/repo", "missing", [])
    summary = RepositorySemanticSearchSummaryBuilder().build(report)
    assert summary.outcome == "no_results"


def test_semantic_search_019_summary_results_found():
    report = RepositorySemanticSearchReport(
        "/repo",
        "worker",
        [
            RepositorySemanticSearchResult(
                "1",
                "symbol",
                "Worker",
                "app.py",
                3,
                0,
                3,
                ["worker"],
            )
        ],
    )
    summary = RepositorySemanticSearchSummaryBuilder().build(report)
    assert summary.outcome == "results_found"


def test_semantic_search_020_serialize_report():
    report = RepositorySemanticSearchReport(
        "/repo",
        "worker",
        [
            RepositorySemanticSearchResult(
                "1",
                "symbol",
                "Worker",
                "app.py",
                3,
                0,
                3,
                ["worker"],
            )
        ],
    )
    response = serialize_repository_semantic_search_report(report)
    assert response.result_count == 1
    assert response.highest_score == 3


def test_semantic_search_021_api_returns_200(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post(
        "/api/v1/repository-semantic-search",
        json={
            "repository_path": str(repo),
            "query": "worker",
        },
    )
    assert response.status_code == 200


def test_semantic_search_022_api_returns_results(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post(
        "/api/v1/repository-semantic-search",
        json={
            "repository_path": str(repo),
            "query": "worker",
        },
    )
    assert response.json()["result_count"] > 0


def test_semantic_search_023_api_returns_summary(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post(
        "/api/v1/repository-semantic-search",
        json={
            "repository_path": str(repo),
            "query": "worker",
        },
    )
    assert response.json()["summary"]["outcome"] == "results_found"


def test_semantic_search_024_api_rejects_missing_path(tmp_path):
    response = client.post(
        "/api/v1/repository-semantic-search",
        json={
            "repository_path": str(tmp_path / "missing"),
            "query": "worker",
        },
    )
    assert response.status_code == 400


def test_semantic_search_025_api_rejects_empty_query(tmp_path):
    repo = make_repo(tmp_path)
    response = client.post(
        "/api/v1/repository-semantic-search",
        json={
            "repository_path": str(repo),
            "query": "",
        },
    )
    assert response.status_code == 422


def test_semantic_search_026_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/repository-semantic-search" in paths


def test_semantic_search_027_route_supports_post():
    route = next(
        route
        for route in app.routes
        if route.path == "/api/v1/repository-semantic-search"
    )
    assert "POST" in route.methods

def test_semantic_search_028_api_alias_expands_fastapi():
    expanded = expand_query_tokens(["api"])
    assert "fastapi" in expanded


def test_semantic_search_029_endpoint_alias_expands_fastapi():
    expanded = expand_query_tokens(["endpoint"])
    assert "api" in expanded
    assert "fastapi" in expanded


def test_semantic_search_030_endpoint_matches_fastapi_document(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositorySemanticSearchEngine().search(
        repo,
        "endpoint",
    )
    assert report.result_count > 0
    assert any(
        "fastapi" in result.matched_terms
        for result in report.results
    )


def test_semantic_search_031_fastapi_direct_query(tmp_path):
    repo = make_repo(tmp_path)
    report = RepositorySemanticSearchEngine().search(
        repo,
        "fastapi",
    )
    assert report.result_count > 0

