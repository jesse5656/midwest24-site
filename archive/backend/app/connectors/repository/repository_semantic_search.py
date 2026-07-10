from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_search_index import (
    RepositorySearchDocument,
    RepositorySearchIndexBuilder,
)


CONCEPT_ALIASES = {
    "api": {
        "endpoint",
        "fastapi",
        "route",
        "router",
        "request",
        "response",
    },
    "class": {"model", "object", "type"},
    "dependency": {"library", "package", "requirement"},
    "function": {"callable", "method", "routine"},
    "import": {"dependency", "module", "package"},
    "repository": {"codebase", "project", "repo"},
    "search": {"find", "lookup", "query", "retrieve"},
    "symbol": {"class", "constant", "function", "method"},
    "test": {"pytest", "spec", "validation", "verification"},
}


def normalize_tokens(value: str) -> list[str]:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    expanded = expanded.replace("_", " ")
    expanded = expanded.replace("-", " ")
    expanded = expanded.replace("/", " ")

    return [
        token.lower()
        for token in re.findall(r"[A-Za-z0-9]+", expanded)
        if token
    ]


def expand_query_tokens(tokens: list[str]) -> set[str]:
    expanded = set(tokens)

    for token in tokens:
        expanded.update(CONCEPT_ALIASES.get(token, set()))

        for concept, aliases in CONCEPT_ALIASES.items():
            if token in aliases:
                expanded.add(concept)
                expanded.update(aliases)

    return expanded


@dataclass(frozen=True)
class RepositorySemanticSearchResult:
    document_id: str
    document_type: str
    title: str
    source: str
    lexical_score: int
    concept_score: int
    total_score: int
    matched_terms: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RepositorySemanticSearchReport:
    repository_path: str
    query: str
    results: list[RepositorySemanticSearchResult] = field(default_factory=list)

    @property
    def result_count(self) -> int:
        return len(self.results)

    @property
    def document_types(self) -> list[str]:
        return sorted({result.document_type for result in self.results})

    @property
    def highest_score(self) -> int:
        if not self.results:
            return 0
        return max(result.total_score for result in self.results)


class RepositorySemanticSearchEngine:
    def search(
        self,
        repository_path: str | Path,
        query: str,
        max_depth: int = 8,
        limit: int = 10,
    ) -> RepositorySemanticSearchReport:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")

        index = RepositorySearchIndexBuilder().build(
            repository_path=root,
            max_depth=max_depth,
        )

        query_tokens = normalize_tokens(query)
        expanded_tokens = expand_query_tokens(query_tokens)

        if not query_tokens:
            return RepositorySemanticSearchReport(
                repository_path=str(root),
                query=query,
                results=[],
            )

        results = [
            result
            for document in index.documents
            if (
                result := self._score_document(
                    document=document,
                    query_tokens=query_tokens,
                    expanded_tokens=expanded_tokens,
                )
            )
            is not None
        ]

        results.sort(
            key=lambda result: (
                -result.total_score,
                -result.lexical_score,
                result.document_id,
            )
        )

        return RepositorySemanticSearchReport(
            repository_path=str(root),
            query=query,
            results=results[:limit],
        )

    def _score_document(
        self,
        document: RepositorySearchDocument,
        query_tokens: list[str],
        expanded_tokens: set[str],
    ) -> RepositorySemanticSearchResult | None:
        document_tokens = normalize_tokens(document.searchable_text)
        document_token_set = set(document_tokens)

        lexical_matches = sorted(set(query_tokens) & document_token_set)
        concept_matches = sorted(
            (expanded_tokens - set(query_tokens)) & document_token_set
        )

        lexical_score = sum(
            document_tokens.count(token) * 3
            for token in lexical_matches
        )
        concept_score = sum(
            document_tokens.count(token)
            for token in concept_matches
        )

        title_tokens = set(normalize_tokens(document.title))
        title_bonus = len(set(query_tokens) & title_tokens) * 2

        total_score = lexical_score + concept_score + title_bonus

        if total_score <= 0:
            return None

        return RepositorySemanticSearchResult(
            document_id=document.document_id,
            document_type=document.document_type,
            title=document.title,
            source=document.source,
            lexical_score=lexical_score,
            concept_score=concept_score,
            total_score=total_score,
            matched_terms=sorted(set(lexical_matches + concept_matches)),
        )
