# START HERE

Version: 1.0.1
Status:
Active

---

## Purpose

This document defines how every engineering session begins.

The repository—not ChatGPT—is the authoritative source of product knowledge.

Every contributor should follow this workflow before beginning work.

---

## Read in Order

1. OPERATING-PLAN.md

2. README.md

3. docs/engineering/ENGINEERING-CONSTITUTION.md

4. archive/docs/product-charter.md

5. Current Sprint / Current Feature

---

## Operating Mode

Execute the Operating Plan.

Do not redesign platform architecture unless an Architecture Change Proposal has been requested.

Finish before expanding.

Engineering before optimization.

Test before documenting.

Maximum three active objectives.

Reality should justify architecture.

---

## Automatic Governed Chat Transition Rule

This rule is mandatory for this workstream and is read from repository
authority during normal session startup.

It does **not** depend on Espanso, a startup alias, conversational memory, or
the user remembering a skill name or special command.

When the user clearly indicates that active work should move to a new, fresh,
replacement, continuation, or otherwise different chat, the assistant shall
automatically execute governed HANDOFF behavior before the transition.

Examples of semantic HANDOFF intent include, but are not limited to:

- start a new chat;
- move this to a new chat;
- move this to a fresh chat;
- hand this off;
- continue this in another chat;
- this chat is getting too long or slow;
- create the continuation for the replacement chat.

The user is **not required** to type `HANDOFF`, `RESUME`,
`$handoff-governed-work`, `:startjr`, `:startarchive`, `:startops`, or any other
trigger token.

HANDOFF shall preserve only the minimum sufficient continuation state,
including as applicable:

- exact workstream identity and scope;
- every materially relevant repository;
- branch, HEAD, upstream, ahead/behind, synchronization, staged, unstaged, and
  untracked state;
- materially relevant governance with exact status;
- current work state;
- the narrowest exact next action, or explicitly `UNRESOLVED`;
- required artifacts and hashes when material;
- material conflicts and unresolved facts;
- security boundaries and secret exclusion.

If the active runtime exposes the validated `handoff-governed-work` skill, use
its HANDOFF mode. If it does not, execute the equivalent governed HANDOFF
procedure directly.

When a replacement chat receives a governed handoff, or the user clearly asks
to continue from one, the assistant shall automatically execute RESUME:

1. treat the handoff as continuation evidence, not repository authority;
2. re-resolve current repository state;
3. reconcile drift, stale claims, and conflicts;
4. determine the exact current next action;
5. continue from the resolved state without restarting broad discovery.

This `START-HERE.md` rule is the workstream activation authority. Text-expansion
aliases may repeat it for convenience but are not required for it to apply.

------------------------------------------------------------------------------

## Session Workflow

Review the Operating Plan.

Execute the highest-priority engineering objective.

Run tests.

Commit completed work.

Update the Operating Plan if priorities changed.

End the session with:

Completed

Current Objective

Next Concrete Step

Deferred

## Pre-Implementation Audit Rule

Before generating any new feature, first audit the repository to determine whether the capability already exists, is partially implemented, or is missing.

Do not generate implementation code until the audit confirms the capability is missing or incomplete.

Use one copy/paste-safe bash block with Python file readers/writers where needed.
Avoid nested heredocs.
Include validation commands.

---

## Repository Philosophy

README.md explains the repository.

START-HERE.md explains how to begin work.

OPERATING-PLAN.md explains what Midwest24 Platform is building now.

---

## Chat Session Archival Standard

Chats are working sessions.

Repositories are institutional memory.

Git commits are historical milestones.

When a chat becomes slow, reaches a natural milestone, or is being replaced, archive it using:

YYYY-MM-DD — Repository — Sprint Name

Example:

2026-07-08 — Midwest24 Archive — Relationship Engine Sprint

---

## Branding Asset Standards

Canonical Midwest24 branding assets are managed under:

```text
assets/branding/
```

The authoritative branding standards are documented in:

```text
assets/branding/README.md
```

That document governs canonical editable logo sources, approved exports, production assets, product-specific assets, archived materials, logo update procedures, and branding governance requirements.

Repository work that creates, modifies, deploys, replaces, or archives branding assets must follow `assets/branding/README.md`.
