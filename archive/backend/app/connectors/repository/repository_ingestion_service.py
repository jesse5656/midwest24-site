from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from app.connectors.repository.filesystem_repository_connector import (
    RepositoryFile,
    RepositoryFilesystemConnector,
)


class RepositoryDocumentIngestor(Protocol):
    def __call__(self, repository_file: RepositoryFile) -> object:
        ...


class RepositoryProcessingJobCreator(Protocol):
    def __call__(self, ingested_document: object, repository_file: RepositoryFile) -> object:
        ...


@dataclass(frozen=True)
class RepositoryIngestionResult:
    discovered_count: int
    ingested_count: int
    processing_job_count: int


class RepositoryIngestionService:
    """
    Wires repository filesystem discovery into the Archive ingestion flow.

    This service intentionally does not parse Git history, inspect commits,
    analyze authorship, or perform code intelligence.

    It also does not bypass the Archive pipeline. Discovered files are passed to
    the provided document ingestor, then the returned document object is passed
    to the provided processing-job creator.
    """

    def __init__(
        self,
        connector: RepositoryFilesystemConnector,
        document_ingestor: RepositoryDocumentIngestor,
        processing_job_creator: RepositoryProcessingJobCreator,
    ) -> None:
        self.connector = connector
        self.document_ingestor = document_ingestor
        self.processing_job_creator = processing_job_creator

    @classmethod
    def from_path(
        cls,
        repository_path: str | Path,
        document_ingestor: RepositoryDocumentIngestor,
        processing_job_creator: RepositoryProcessingJobCreator,
    ) -> "RepositoryIngestionService":
        return cls(
            connector=RepositoryFilesystemConnector(repository_path),
            document_ingestor=document_ingestor,
            processing_job_creator=processing_job_creator,
        )

    def ingest(self) -> RepositoryIngestionResult:
        discovered = self.connector.discover()

        ingested_count = 0
        processing_job_count = 0

        for repository_file in discovered:
            ingested_document = self.document_ingestor(repository_file)
            ingested_count += 1

            self.processing_job_creator(ingested_document, repository_file)
            processing_job_count += 1

        return RepositoryIngestionResult(
            discovered_count=len(discovered),
            ingested_count=ingested_count,
            processing_job_count=processing_job_count,
        )
