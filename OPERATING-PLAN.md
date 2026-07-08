# Midwest24 Platform Operating Plan

Version: 1.0.0

Status:
Active

------------------------------------------------------------------------------

## Purpose

This document governs the current engineering priorities for the Midwest24 Platform.

The Engineering Constitution defines how engineering is performed.

The Operating Plan defines what is currently being built.

------------------------------------------------------------------------------

# Current Phase

Archive Foundation

Goal:

Develop Midwest24 Archive into a traceable institutional memory platform that validates the research of the Systems Architect Discipline.

------------------------------------------------------------------------------

# Current Objectives

## Objective 1

Research Program 001 Support

Deliverables

□ Knowledge lineage

□ Evidence relationships

□ Primary source support

□ Traceability

------------------------------------------------------------------------------

## Objective 2

Archive Core Development

Deliverables

□ Entity model

□ Relationship engine

□ Evidence model

□ Timeline support

□ Search foundation

------------------------------------------------------------------------------

## Objective 3

Engineering Discipline

Deliverables

□ Automated testing

□ CI/CD

□ Documentation

□ Architecture validation

------------------------------------------------------------------------------


------------------------------------------------------------------------------

# Execution Mode

## Sprint-Based Execution

Status:
Active

Purpose:
Increase development velocity without abandoning architecture discipline.

The prior one-objective-per-session workflow is replaced with one coherent sprint per session.

A sprint may include multiple related implementation steps, multiple tests, multiple commits, and documentation updates, provided they all support one architectural capability.

Rules:
- Do not redesign architecture unless an Architecture Change Proposal is explicitly requested.
- Do not mix unrelated capabilities in one sprint.
- Prefer 8–15 related engineering changes per sprint when the repository state supports it.
- Tests must pass before sprint completion.
- The Operating Plan must be updated before sprint completion.
- Each sprint must end with a clear next sprint objective.

Sprint Completion Criteria:
- Planned capability implemented.
- Relevant tests added or improved.
- Full test suite passing.
- Documentation or runbook updated when behavior changes.
- Changes committed.
- Next sprint objective recorded.

Velocity Rule:
Optimize for larger coherent engineering batches instead of tiny one-test increments.

# Weekly Cadence

- Complete one coherent engineering sprint
- Add or improve a meaningful test group
- Reduce technical debt inside the sprint scope
- Validate architecture through implementation
- Prefer capability-level progress over isolated micro-objectives

------------------------------------------------------------------------------

# Parking Lot

- Future applications
- Human Operating System
- Additional research programs
- Nonessential platform features

------------------------------------------------------------------------------

# Decision Rules

Execute the Operating Plan.

Engineering before optimization.

Reality should justify architecture.

Research drives software.

Software validates research.

------------------------------------------------------------------------------

# Definition of Success

Success is measured by increasing the platform's ability to preserve, relate, discover, and transfer organizational capability.


---

## Session Update

Status:
- Semantic search pipeline test stabilized.
- Archive test suite passing at 27 tests.
- pgvector embedding storage is active.
- Embedding provider registry is in place.
- Smoke pipeline is operational.

Next Highest-Priority Objective:
- Add semantic search result enrichment so search results include document, entity, and source context instead of only chunk text and distance.

---

## Session Update

Status:
- Semantic search pipeline test stabilized.
- Archive test suite passing at 27 tests.
- pgvector embedding storage is active.
- Embedding provider registry is in place.
- Smoke pipeline is operational.

Next Highest-Priority Objective:
- Add semantic search result enrichment so search results include document, entity, and source context instead of only chunk text and distance.

---

## Session Update

Status:
- Semantic search pipeline test stabilized.
- Archive test suite passing at 27 tests.
- pgvector embedding storage active.
- Embedding provider registry active.
- Smoke pipeline operational.

Next Highest-Priority Objective:
- Enrich semantic search results with document, entity, and source context.

---

## Archive Connector Workflow

Status:
Active

Purpose:
Define the standard workflow for adding new knowledge-source connectors to Midwest24 Archive.

Workflow:
1. Verify repository state.
2. Read START-HERE.md.
3. Read OPERATING-PLAN.md.
4. Identify the next highest-priority connector.
5. Inspect existing connector interfaces.
6. Implement the smallest connector capability.
7. Add tests.
8. Run the full test suite.
9. Commit the connector work.
10. Update OPERATING-PLAN.md with status and next step.

Connector Standard:
- Every connector must implement discovery.
- Every connector must support future ingestion into Archive.
- Every connector must have at least one automated test.
- Connectors must not bypass the Archive ingestion pipeline.

Current Connector Capability:
- FilesystemConnector added.
- Connector framework established.
- Test suite passing at 28 tests.

Next Highest-Priority Connector:
- Repository filesystem ingestion for local knowledge repositories.


------------------------------------------------------------------------------

# Session Management

When conversation performance degrades or a milestone is reached:

□ Commit completed work.

□ Update this Operating Plan if priorities changed.

□ Archive the chat using the naming standard in START-HERE.md.

□ Begin the next session from START-HERE.md.


---

## Session Update

Status:
- Repository filesystem ingestion connector added.
- Connector discovers supported files from local knowledge repositories.
- Connector excludes `.git`, runtime, dependency, cache, and build directories.
- Repository file metadata is captured for future Archive ingestion.
- Automated tests added for discovery, exclusions, metadata, missing paths, and invalid paths.

Completed:
- Repository filesystem ingestion discovery only.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Wire discovered repository files into the existing Archive document ingestion pipeline without bypassing processing jobs, text extraction, chunking, embeddings, or semantic search enrichment.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Repository filesystem ingestion has been wired into the Archive ingestion flow.
- Repository discovery now feeds a document ingestion callback.
- Each ingested repository file now triggers a processing-job callback.
- The connector still does not bypass the Archive pipeline.
- Automated tests added for repository ingestion wiring and connector filtering before ingestion.

Completed:
- Repository filesystem ingestion wiring only.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Replace the test callback boundary with the concrete Archive document creation and processing-job creation services already used by normal document ingestion.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Repository ingestion command boundary added.
- Local repository paths can now be passed into the repository ingestion service from a CLI entrypoint.
- CLI currently preserves the ingestion boundary and does not bypass the Archive pipeline.
- Automated CLI coverage added.

Completed:
- Repository ingestion command boundary.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Replace the CLI test callbacks with concrete Archive document creation and processing-job creation services.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Repository filesystem ingestion now writes into the real Archive pipeline.
- Supported repository files are copied into Archive document storage.
- Repository files create real Document records tied to an entity.
- Each repository-created Document now receives a real ProcessingJob.
- No Git history, blame, commit graph, branch, authorship, or code intelligence was added.

Completed:
- Repository filesystem ingestion into Archive document and processing-job pipeline.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Add an API endpoint or management command that accepts an entity ID and repository path, then invokes ArchiveRepositoryIngestor.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Repository filesystem ingestion now writes into the real Archive pipeline.
- Supported repository files are copied into Archive document storage.
- Repository files create real Document records tied to an entity.
- Each repository-created Document now receives a real ProcessingJob.
- No Git history, blame, commit graph, branch, authorship, or code intelligence was added.

Completed:
- Repository filesystem ingestion into Archive document and processing-job pipeline.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Add an API endpoint or management command that accepts an entity ID and repository path, then invokes ArchiveRepositoryIngestor.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Repository filesystem ingestion now writes into the real Archive pipeline.
- Supported repository files are copied into Archive document storage.
- Repository files create real Document records tied to an entity.
- Each repository-created Document now receives a real ProcessingJob.
- No Git history, blame, commit graph, branch, authorship, or code intelligence was added.

Completed:
- Repository filesystem ingestion into Archive document and processing-job pipeline.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Add an API endpoint or management command that accepts an entity ID and repository path, then invokes ArchiveRepositoryIngestor.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Repository ingestion API endpoint added.
- API accepts an entity ID and local repository path.
- API invokes ArchiveRepositoryIngestor and creates real Document and ProcessingJob records.
- API database dependency corrected to use the existing app API context.
- Automated API coverage added for successful ingestion and unknown entity rejection.

Completed:
- Repository ingestion API boundary.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Add a worker-backed smoke test that ingests a repository markdown file, processes the generated job, and verifies searchable chunks/embeddings are created.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Repository ingestion API endpoint added.
- API accepts an entity ID and local repository path.
- API invokes ArchiveRepositoryIngestor and creates real Document and ProcessingJob records.
- API database dependency corrected to use the existing app API context.
- Automated API coverage added for successful ingestion and unknown entity rejection.

Completed:
- Repository ingestion API boundary.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Add a worker-backed smoke test that ingests a repository markdown file, processes the generated job, and verifies text, chunks, and embeddings are created.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Worker-backed repository ingestion smoke test added.
- Repository markdown ingestion now verifies the full path from API ingestion to Document, ProcessingJob, DocumentWorker, text extraction, chunk creation, and embedding storage.
- Test confirms generated processing jobs complete successfully.

Completed:
- Repository ingestion worker smoke pipeline.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Add semantic-search verification for repository-ingested content so repository knowledge can be discovered through the existing semantic search API.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Repository-ingested markdown semantic search verification added.
- Test confirms repository ingestion creates searchable chunks through the existing semantic search API.
- Semantic search response verifies repository entity context, filename, chunk text, chunk ID, document ID, and distance.

Completed:
- Repository ingestion semantic search verification.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Add repository ingestion documentation and a minimal runbook for ingesting local knowledge repositories safely.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Repository ingestion runbook added.
- Runbook documents current filesystem-only scope, API usage, safety rules, and completion criteria.
- Git history and code intelligence remain explicitly deferred.

Completed:
- Repository ingestion documentation and minimal runbook.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Add controlled repository ingestion allowlist or path validation before broad local repository ingestion is used outside development.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Repository path validation added before Archive ingestion.
- Invalid, hidden, and non-directory paths are rejected.
- Repository ingestion security boundary established.

Completed:
- Repository ingestion path validation.

Current Objective:
- Archive Core Development.

Next Concrete Step:
- Introduce configurable repository allowlists for production deployments.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Operating Plan execution mode upgraded from micro-objective execution to sprint-based execution.
- Future sessions should complete one coherent engineering sprint instead of stopping after every small objective.
- Sprint mode allows multiple related commits, tests, implementation steps, and documentation updates under one architectural capability.
- Architecture discipline remains unchanged: no redesign without an explicit Architecture Change Proposal.

Completed:
- Operating Plan sprint-execution upgrade.

Current Objective:
- Archive Core Development.

Next Sprint Objective:
- Repository Ingestion Hardening Sprint.

Sprint Scope:
- Path validation.
- Repository allowlist.
- Configuration-driven allowed roots.
- API validation failures.
- Tests for rejected paths.
- Tests for allowed paths.
- Runbook update.
- Full suite verification.

Deferred:
- Git history ingestion.
- Git blame.
- Commit graph analysis.
- Branch analysis.
- Authorship timelines.
- Code intelligence and language parsing.
