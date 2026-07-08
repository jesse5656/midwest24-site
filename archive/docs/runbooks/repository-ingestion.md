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
