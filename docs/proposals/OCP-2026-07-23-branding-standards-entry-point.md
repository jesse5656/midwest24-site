# Operational Change Proposal

Version: 1.0.0

Status: Approved

---

## Title

Reference the Midwest24 branding standards from the repository entry point.

## Purpose

Make the canonical Midwest24 branding standards discoverable from `START-HERE.md`.

## Classification

Operational documentation change.

This proposal does not alter product architecture, application behavior, deployment behavior, or the repository governance system.

## Scope

- `START-HERE.md`

## Authorized Change

Add a Branding Asset Standards section to `START-HERE.md` that directs contributors to `assets/branding/README.md` as the authoritative branding asset standard.

## Rationale

The branding asset structure and workflow are already established and documented. Referencing that documentation from the repository entry point improves discoverability and ensures contributors locate the authoritative branding rules before changing brand assets.

## Impact

- Documentation only.
- No application code changes.
- No architecture changes.
- No deployment changes.
- No governance enforcement changes.

## Validation

- Confirm `START-HERE.md` references `assets/branding/README.md`.
- Run `python3 scripts/governance/governance_engine.py`.
- Review the complete staged diff before committing.
