# Repository Ingestion Runbook

Status: Active

Purpose:
Safely ingest local knowledge repositories into Midwest24 Archive without bypassing the Archive document, processing-job, worker, chunking, embedding, and semantic-search pipeline.

## Scope

Repository ingestion currently supports filesystem-based ingestion only.

It does:
- discover supported files from a local repository
- exclude runtime, dependency, cache, build, and `.git` directories
- copy supported files into Archive document storage
- create Archive `Document` records
- create `ProcessingJob` records
- allow workers to extract text, create chunks, create embeddings, and expose content through semantic search

It does not:
- read Git history
- inspect Git blame
- analyze commit graphs
- analyze branches
- build authorship timelines
- perform code intelligence or language parsing

## API Endpoint

POST /api/v1/repository-ingestions

Request:

{
  "entity_id": "ENTITY_UUID",
  "repository_path": "/absolute/path/to/local/repository"
}

Response:

{
  "discovered_count": 1,
  "document_count": 1,
  "processing_job_count": 1
}

## Safety Rules

- Ingest only trusted local repositories.
- Do not ingest secrets, `.env` files, private keys, credentials, or machine-local configuration.
- Review repository contents before ingestion.
- Keep `.git` history deferred until a separate Git-ingestion milestone exists.
- Do not bypass the processing-job pipeline.

## Completion Criteria

A repository ingestion milestone is complete only when:
- tests pass
- repository files create real `Document` records
- repository files create real `ProcessingJob` records
- worker processing creates text, chunks, and embeddings
- semantic search can discover repository-ingested content
- Operating Plan is updated
- changes are committed


------------------------------------------------------------------------------

## Repository Ingestion Observability

Repository ingestion now returns observable execution metadata.

Current response fields:

- discovered_count
- document_count
- processing_job_count
- bytes_ingested
- elapsed_ms
- skipped_count
- unsupported_count
- failures

Repository ingestion also logs start, file-level failures, and completion.


------------------------------------------------------------------------------

## Processing Job Status Observability

Repository ingestion responses now include processing job status counts.

The `processing_jobs_by_status` object reports:

- pending
- running
- completed
- failed
- total

This allows operators to distinguish ingestion success from downstream worker progress.


------------------------------------------------------------------------------

## Skipped and Unsupported File Observability

Repository ingestion now distinguishes between supported files, skipped paths, and unsupported files.

Supported files:
- Files that match the repository ingestion suffix allowlist and are eligible for Archive document creation.

Skipped paths:
- Directories skipped because they are excluded runtime, dependency, cache, build, or `.git` paths.

Unsupported files:
- Files discovered in the repository but not eligible for ingestion because their extension is not currently supported.

The API response includes:

- skipped_count
- unsupported_count
- skipped_paths
- unsupported_files

This lets operators understand what was intentionally ignored during repository ingestion.


------------------------------------------------------------------------------

## Duplicate Ingestion Observability

Repository ingestion now detects duplicate repository files per entity.

Duplicate rule:

- A repository file is considered duplicate when a `Document` already exists for the same entity with the same repository-relative filename.

Duplicate behavior:

- Duplicate files are not copied again.
- Duplicate files do not create new `Document` records.
- Duplicate files do not create new `ProcessingJob` records.
- Duplicate files are reported in the ingestion response.

The API response includes:

- duplicate_count
- duplicate_files

This makes repeat ingestion idempotent at the repository-relative filename level while preserving separate ingestion for different entities.


------------------------------------------------------------------------------

## Duplicate Ingestion Observability

Repository ingestion detects duplicate repository files per entity.

Duplicate rule:

- A repository file is duplicate when a Document already exists for the same entity with the same repository-relative filename.

Duplicate behavior:

- Duplicate files are not copied again.
- Duplicate files do not create new Document records.
- Duplicate files do not create new ProcessingJob records.
- Duplicate files are reported in the ingestion response.

The API response includes:

- duplicate_count
- duplicate_files


------------------------------------------------------------------------------

## Failure Observability

Repository ingestion reports file-level copy failures without stopping the full ingestion run.

Failure behavior:

- A failed file is reported in `failures`.
- A failed file does not create a `Document`.
- A failed file does not create a `ProcessingJob`.
- Failed file bytes are not counted in `bytes_ingested`.
- The database session is rolled back after a failed file so the next file can continue.
- Repository ingestion logs start, file failure, and finish events.


------------------------------------------------------------------------------

## Failure Observability

Repository ingestion reports file-level copy failures without stopping the full ingestion run.

Failure behavior:

- A failed file is reported in `failures`.
- A failed file does not create a `Document`.
- A failed file does not create a `ProcessingJob`.
- Failed file bytes are not counted in `bytes_ingested`.
- The database session is rolled back after a failed file so the next file can continue.
- Repository ingestion logs start, file failure, and finish events.


------------------------------------------------------------------------------

## Incremental Ingestion API Serialization

The incremental ingestion API serializes nested repository ingestion reports into the public response schema.

This keeps internal dataclass reports separate from API response models while preserving operator-facing metadata.


------------------------------------------------------------------------------

## Repository Objective Summary

Repository ingestion now includes objective-level summary primitives.

Objective summaries aggregate repository ingestion reports and expose:

- objective_name
- status
- total_documents
- total_processing_jobs
- total_failures
- total_duplicates
- total_unsupported
- total_skipped
- action_required
- is_complete

This provides a final operator-facing rollup for closing the Repository Ingestion Observability objective.
