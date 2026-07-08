from __future__ import annotations

import argparse
from pathlib import Path

from app.connectors.repository import RepositoryIngestionService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Discover repository files and pass them into the Archive ingestion flow."
    )
    parser.add_argument(
        "repository_path",
        help="Path to the local knowledge repository to ingest.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    repository_path = Path(args.repository_path).expanduser().resolve()

    discovered_documents = []
    processing_jobs = []

    def document_ingestor(repository_file):
        document = {
            "source_type": "repository_file",
            "source_path": repository_file.relative_path,
            "absolute_path": str(repository_file.path),
            "size_bytes": repository_file.size_bytes,
            "suffix": repository_file.suffix,
        }
        discovered_documents.append(document)
        return document

    def processing_job_creator(ingested_document, repository_file):
        job = {
            "source_type": "repository_file",
            "source_path": repository_file.relative_path,
            "document": ingested_document,
            "pipeline": "archive_processing",
        }
        processing_jobs.append(job)
        return job

    service = RepositoryIngestionService.from_path(
        repository_path=repository_path,
        document_ingestor=document_ingestor,
        processing_job_creator=processing_job_creator,
    )

    result = service.ingest()

    print(f"Repository path: {repository_path}")
    print(f"Discovered files: {result.discovered_count}")
    print(f"Ingested documents: {result.ingested_count}")
    print(f"Processing jobs created: {result.processing_job_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
