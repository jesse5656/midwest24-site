# Operational Change Proposal

Version: 1.0.0

Status: Approved

---

## Title

Automatic governed chat HANDOFF and RESUME from repository startup authority.

## Purpose

Ensure this workstream does not depend on the user remembering an Espanso
alias, skill name, `HANDOFF`, `RESUME`, or another special trigger when moving
active governed work between chats.

## Classification

Operational startup/governance documentation change.

This proposal does not alter product architecture, application behavior,
deployment behavior, or the repository governance hierarchy.

## Scope

- `docs/proposals/OCP-2026-09-04-AUTOMATIC-GOVERNED-CHAT-TRANSITION.md`
- `START-HERE.md`

## Authorized Change

Add the mandatory Automatic Governed Chat Transition Rule to `START-HERE.md`.

Clear semantic intent to move active work to another chat automatically
requires HANDOFF. Receipt of a governed handoff, or a clear request to continue
from it, automatically requires RESUME.

`START-HERE.md` is the trigger authority. Espanso and other aliases are optional
convenience mechanisms only.

## Rationale

The validated handoff methodology exists to remove dependence on conversational
memory and user reconstruction. Requiring the user to remember another trigger
would recreate the dependency the methodology is intended to eliminate.

## Validation

- Confirm `START-HERE.md` contains the automatic transition rule.
- Confirm aliases and special commands are explicitly not required.
- Run Repository Context Resolution when available.
- Run Governance Enforcement against the staged change.
- Review the exact staged diff before committing.

## Approval

Approved by explicit governing user direction on 2026-09-04.
