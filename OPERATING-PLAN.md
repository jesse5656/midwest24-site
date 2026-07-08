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

# Weekly Cadence

- Complete one engineering milestone
- Improve one test
- Reduce technical debt
- Validate architecture through implementation

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
