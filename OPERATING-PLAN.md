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
