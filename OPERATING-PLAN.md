# Midwest24 Platform Operating Plan

Version: 1.1.0

Status:
Active

------------------------------------------------------------------------------

## Purpose

This document defines current execution for the Midwest24 Platform.

------------------------------------------------------------------------------

# Current Objective

Type:
Engineering Sprint

Name:
Repository Ingestion Observability

Status:
In Progress

Objective:
Improve operational visibility into repository ingestion without changing the ingestion architecture.

Scope:
- Ingestion logging
- Result metadata
- Failure diagnostics
- Processing-job statistics
- API response improvements
- End-to-end observability tests
- Runbook updates

Success Criteria:
- Repository ingestion behavior is easier to observe and troubleshoot
- Tests pass
- Documentation or runbook updated if behavior changed
- OPERATING-PLAN.md reflects current execution state

Definition of Done:
□ Objective completed
□ Validation completed
□ Verification completed through tests
□ Documentation updated
□ OPERATING-PLAN.md updated
□ Git commit completed if repository changes occurred

------------------------------------------------------------------------------

# Priority Queue

1. Git Repository Intelligence
2. Repository Change Detection
3. Connector Scheduling
4. Knowledge Graph Construction
5. Entity Resolution Improvements
6. AI-Assisted Repository Summarization

------------------------------------------------------------------------------

# Session Management

When Current Objective is complete:

1. Verify against Definition of Done.
2. Update OPERATING-PLAN.md.
3. Promote Priority Queue item #1 if appropriate.
4. Commit changes.
5. Stop.


---

# Current Objective

Type:
Engineering Sprint

Name:
Repository Ingestion Observability

Status:
In Progress

Objective:
Make repository ingestion observable and diagnosable without changing the ingestion architecture.

Scope:
- Expanded ingestion result metadata
- Elapsed time tracking
- Bytes ingested tracking
- Structured skipped-file reporting
- Unsupported extension reporting
- API response expansion
- Logging for ingestion start, finish, and failure
- Tests for observable ingestion results
- Runbook update

Success Criteria:
- Repository ingestion reports documents, jobs, bytes, elapsed time, skipped files, unsupported files, and failures.
- API exposes expanded ingestion metadata.
- Tests pass.
- Runbook documents observability behavior.

Definition of Done:

□ Objective completed

□ Validation completed

□ Verification completed

□ Documentation updated

□ OPERATING-PLAN.md updated

□ Git commit completed

------------------------------------------------------------------------------

# Priority Queue

1. Git Repository Intelligence
2. Repository Change Detection
3. Connector Scheduling
4. Knowledge Graph Construction
5. Entity Resolution Improvements
6. AI Repository Summarization


---

## Session Update

Status:
- Repository Ingestion Observability Sprint completed.
- Ingestion report model added.
- Failure report model added.
- Ingestion now reports bytes ingested and elapsed milliseconds.
- API response expanded with observable metadata.
- Repository ingestion logging added.
- Observability tests added.
- Repository ingestion runbook updated.

Completed:
- Repository Ingestion Observability.

Current Objective:
- Archive Core Development.

Next Objective:
- Promote the next item from Priority Queue into Current Objective.

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
- Repository ingestion observability expanded with processing-job status statistics.
- Repository ingestion response now reports pending, running, completed, failed, and total processing-job counts.
- Job-statistics tests added.
- API and observability tests updated.
- Repository ingestion runbook updated.

Completed:
- Repository ingestion processing-job observability.

Current Objective:
- Repository Ingestion Observability.

Next Concrete Step:
- Add skipped-file and unsupported-extension observability.

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
- Repository ingestion observability expanded with skipped-path and unsupported-file reporting.
- Filesystem connector now supports discover_with_report while preserving legacy discover behavior.
- Discovery report model added.
- API response now includes skipped_paths and unsupported_files.
- Tests added for discovery reporting, ingestion reporting, API reporting, and legacy discover compatibility.
- Repository ingestion runbook updated.

Completed:
- Repository ingestion skipped-file and unsupported-extension observability.

Current Objective:
- Repository Ingestion Observability.

Next Concrete Step:
- Add duplicate-ingestion detection and observable duplicate reporting.

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
- Repository ingestion duplicate detection added.
- Duplicate repository files are now detected per entity by repository-relative filename.
- Duplicate files are reported instead of copied again.
- Duplicate files no longer create extra Document records or ProcessingJob records.
- API response now includes duplicate_count and duplicate_files.
- Tests added for duplicate detection, entity scoping, duplicate ingestion behavior, API duplicate reporting, job-status behavior on duplicates, and report shape.
- Repository ingestion runbook updated.

Completed:
- Repository ingestion duplicate detection and observable duplicate reporting.

Current Objective:
- Repository Ingestion Observability.

Next Concrete Step:
- Add failure injection and copy-failure observability coverage.

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
- Repository ingestion duplicate detection added.
- Duplicate repository files are detected per entity by repository-relative filename.
- Duplicate files are reported instead of copied again.
- Duplicate files no longer create extra Document records or ProcessingJob records.
- API response includes duplicate_count and duplicate_files.
- Repository ingestor rewritten deterministically to remove patch drift.
- Repository ingestion runbook updated.

Completed:
- Repository ingestion duplicate detection and observable duplicate reporting.

Current Objective:
- Repository Ingestion Observability.

Next Concrete Step:
- Add failure injection and copy-failure observability coverage.

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
- Repository ingestion failure observability stabilized.
- Failure tests now scope database assertions to the entity under test.
- Logging tests now explicitly capture INFO-level ingestion start and finish logs.
- Repository-ingested content verification now checks worker-created text, chunks, and embeddings directly.
- Repository ingestion runbook updated.

Completed:
- Repository ingestion failure observability stabilization.

Current Objective:
- Repository Ingestion Observability.

Next Concrete Step:
- Add operator-facing summary fields and finalize Repository Ingestion Observability objective.

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
- Repository ingestion failure observability stabilized.
- Failure tests now scope database assertions to the entity under test.
- Logging tests now explicitly capture INFO-level ingestion start and finish logs.
- Repository-ingested content verification now checks worker-created text, chunks, and embeddings directly.
- Repository ingestion runbook updated.

Completed:
- Repository ingestion failure observability stabilization.

Current Objective:
- Repository Ingestion Observability.

Next Concrete Step:
- Add operator-facing summary fields and finalize Repository Ingestion Observability objective.

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
- Incremental repository ingestion API serialization fixed.
- Nested ingestion reports are now converted into RepositoryIngestionResponse.
- Incremental API tests restored from debug instrumentation.
- Incremental API now exposes nested document count and processing-job status metadata.

Completed:
- Incremental repository ingestion API serialization.

Current Objective:
- Repository Ingestion Observability.

Next Concrete Step:
- Finalize operator-facing summary fields and close Repository Ingestion Observability objective.

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
- Repository objective summary primitives added.
- Objective summary builder can aggregate normal ingestion reports.
- Objective summary builder can aggregate incremental ingestion reports.
- Objective summary schema added.
- Tests added for totals, failures, duplicates, empty report lists, incremental reports, and schema serialization.
- Repository ingestion runbook updated.

Completed:
- Repository objective summary primitives.

Current Objective:
- Repository Ingestion Observability.

Next Concrete Step:
- Close Repository Ingestion Observability objective and promote the next Priority Queue item.

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
- Repository objective readiness primitives added.
- Repository objective closeout primitives added.
- Readiness schemas added.
- Tests added for readiness reports, readiness evaluator, closeout builder, schemas, integration behavior, exports, and operator-readable messages.
- Repository ingestion runbook updated.

Completed:
- Repository objective readiness and closeout primitives.

Current Objective:
- Repository Ingestion Observability.

Next Concrete Step:
- Mark Repository Ingestion Observability complete and promote Git Repository Intelligence from the Priority Queue.

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
- Git Repository Intelligence primitives added.
- Git command runner added.
- Git repository detector added.
- Git commit parser added.
- Git history reader added.
- Git status reader added.
- Git branch reader added.
- Git repository summary builder added.
- Tests added for command results, commit parsing, history reader, status reader, branch reader, repository detector, and summary builder.
- Repository ingestion runbook updated.

Completed:
- Git Repository Intelligence primitives.

Current Objective:
- Git Repository Intelligence.

Next Concrete Step:
- Add Git intelligence API endpoint and operator-facing summary schema.

Deferred:
- Git blame.
- Commit graph analysis.
- Branch analysis beyond local branch summary.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Git Repository Intelligence API added.
- Git repository intelligence schema added.
- Git operator summary builder added.
- API serialization helpers added.
- Git intelligence route registered.
- Tests added for summary building, schemas, serialization, endpoint behavior, error handling, exports, and route registration.
- Repository ingestion runbook updated.

Completed:
- Git Repository Intelligence API endpoint and operator summary.

Current Objective:
- Git Repository Intelligence.

Next Concrete Step:
- Add commit history ingestion preview without persisting Git history.

Deferred:
- Git blame.
- Commit graph analysis.
- Branch analysis beyond local branch summary.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Git commit preview primitives added.
- Git commit preview API added.
- Git commit preview schemas added.
- Git commit preview operator summary added.
- Route registered in app main.
- Tests added for preview model, summary builder, schemas, serialization, API behavior, route registration, and exports.
- Repository ingestion runbook updated.

Completed:
- Git commit preview API.

Current Objective:
- Git Repository Intelligence.

Next Concrete Step:
- Add Git file-change preview from commit history without persisting Git history.

Deferred:
- Git blame.
- Commit graph analysis.
- Branch analysis beyond local branch summary.
- Authorship timelines.
- Code intelligence and language parsing.


---

## Session Update

Status:
- Git file-change preview primitives added.
- Git file-change preview API added.
- Git file-change schemas added.
- Git file-change operator summary added.
- Route registered in app main.
- Tests added for file-change models, parser, builder, summary, schemas, serialization, API behavior, route registration, and exports.
- Repository ingestion runbook updated.

Completed:
- Git file-change preview API.

Current Objective:
- Git Repository Intelligence.

Next Concrete Step:
- Add Git authorship preview without persisting author timelines.

Deferred:
- Git blame.
- Commit graph analysis.
- Branch analysis beyond local branch summary.
- Authorship timelines persistence.
- Code intelligence and language parsing.
