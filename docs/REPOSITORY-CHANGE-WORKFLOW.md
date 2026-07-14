# Repository Change Workflow

Version: 1.0.0

Status:
Active

------------------------------------------------------------------------------

## Purpose

This procedure defines the required workflow for changes to the
Midwest24 Product Engineering repository.

------------------------------------------------------------------------------

## Governing Principle

The repository is the authoritative source of truth.

Implementation shall be informed by the applicable repository context.

Automate deterministic process.

Preserve human judgment.

------------------------------------------------------------------------------

## Canonical Change Workflow

Intent to Change Repository

↓

Repository Context Resolution

↓

Engineering, Research, or Operational Work

↓

Governance Enforcement

↓

Commit

------------------------------------------------------------------------------

## Entry Gate — Repository Context Resolution

Repository Context Resolution is required before work intended to modify
the repository begins.

It resolves applicable:

- repository identity and Git state;
- Operating Plan;
- current objective or active sprint;
- governance;
- Engineering Standards;
- Operational Procedures;
- Implementation Guides;
- AI Collaboration Standards;
- protected assets;
- active ACPs and OCPs;
- warnings.

Run:

```bash
python3 scripts/platform/repository_context.py
```

Machine-readable output:

```bash
python3 scripts/platform/repository_context.py --format json
```

Repository Context Resolution provides context.

It does not make architectural decisions.

------------------------------------------------------------------------------

## Exit Gate — Governance Enforcement

Governance Enforcement checks deterministic, machine-verifiable
governance requirements before governed changes are committed.

Run against staged changes:

```bash
python3 scripts/governance/governance_engine.py --staged
```

Protected changes require an approved ACP or OCP.

A proposal may be supplied with:

```bash
GOVERNANCE_PROPOSAL=path/to/approved-proposal.md         git commit -m "commit message"
```

Governance Enforcement does not evaluate architectural quality.

------------------------------------------------------------------------------

## Policy Validation

Run:

```bash
python3 scripts/governance/validate_governance_policy.py
```

The authoritative governance remains the repository's normative
documents.

`.governance/policy.yaml` is only the executable representation of the
machine-verifiable subset.

------------------------------------------------------------------------------

## Human Responsibility

Architectural judgment, constitutional interpretation, engineering
tradeoffs, research conclusions, and strategic decisions remain human
responsibilities.
