from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.repository_knowledge_graph import (
    RepositoryKnowledgeGraphBuilder,
)


@dataclass(frozen=True)
class RepositorySearchDocument:
    document_id: str
    document_type: str
    title: str
    body: str
    source: str

    @property
    def searchable_text(self) -> str:
        return f"{self.title} {self.body} {self.source}".lower()


@dataclass(frozen=True)
class RepositorySearchResult:
    document_id: str
    document_type: str
    title: str
    source: str
    score: int


@dataclass(frozen=True)
class RepositorySearchIndex:
    repository_path: str
    documents: list[RepositorySearchDocument] = field(default_factory=list)

    @property
    def document_count(self) -> int:
        return len(self.documents)

    @property
    def document_types(self) -> list[str]:
        return sorted({document.document_type for document in self.documents})

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[RepositorySearchResult]:
        terms = [
            term.strip().lower()
            for term in query.split()
            if term.strip()
        ]

        if not terms:
            return []

        results: list[RepositorySearchResult] = []

        for document in self.documents:
            score = sum(
                document.searchable_text.count(term)
                for term in terms
            )

            if score <= 0:
                continue

            results.append(
                RepositorySearchResult(
                    document_id=document.document_id,
                    document_type=document.document_type,
                    title=document.title,
                    source=document.source,
                    score=score,
                )
            )

        return sorted(
            results,
            key=lambda result: (-result.score, result.document_id),
        )[:limit]


class RepositorySearchIndexBuilder:
    def build(
        self,
        repository_path: str | Path,
        max_depth: int = 8,
    ) -> RepositorySearchIndex:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(
                f"Repository path does not exist: {root}"
            )

        if not root.is_dir():
            raise NotADirectoryError(
                f"Repository path is not a directory: {root}"
            )

        graph = RepositoryKnowledgeGraphBuilder().build(
            root,
            max_depth=max_depth,
        )

        documents: list[RepositorySearchDocument] = []

        for node in graph.nodes:
            documents.append(
                RepositorySearchDocument(
                    document_id=node.node_id,
                    document_type=node.node_type,
                    title=node.label,
                    body=f"{node.node_type} from {node.source}",
                    source=node.source,
                )
            )

        for edge in graph.edges:
            document_id = (
                f"edge:{edge.source_id}->"
                f"{edge.target_id}:{edge.relationship}"
            )

            documents.append(
                RepositorySearchDocument(
                    document_id=document_id,
                    document_type="relationship",
                    title=edge.relationship,
                    body=(
                        f"{edge.source_id} "
                        f"{edge.relationship} "
                        f"{edge.target_id}"
                    ),
                    source=edge.source_id,
                )
            )

        return RepositorySearchIndex(
            repository_path=str(root),
            documents=sorted(
                documents,
                key=lambda document: document.document_id,
            ),
        )
