# Contributing to Midwest24 Core

## Purpose

This repository serves as the primary engineering repository for the Midwest24 Core platform.

Every change should improve one or more of the following:

- Reliability
- Security
- Maintainability
- Documentation
- Scalability
- Operational Efficiency

---

# Engineering Philosophy

Midwest24 Core follows several guiding principles.

## Documentation First

Every significant feature, application, integration, migration, or architectural decision must be documented.

No production system should exist without accompanying documentation.

---

## Infrastructure as Documentation

Infrastructure should be understandable through version-controlled documentation.

Every major application should include:

- API notebook
- Runbook
- Architecture documentation
- Operational procedures

---

## Simplicity

Prefer simple, maintainable solutions over unnecessary complexity.

Avoid introducing dependencies without clear operational benefit.

---

## Security by Default

Security is considered during design rather than added afterward.

Examples include:

- Least privilege
- Phishing-resistant MFA
- Passkeys
- Authentik SSO
- Encryption
- Secure backups

---

# Repository Organization

```
Website

Engineering Documentation

Operations Manual

Automation

Infrastructure

Diagrams

Runbooks

API Notebooks
```

Each document should have one primary purpose.

---

# Documentation Standards

Documentation should answer:

What?

Why?

How?

Verification

Rollback

Related documentation

---

# Git Workflow

Before committing:

```
git status --short
```

Review changes carefully.

Commit related changes together.

Avoid mixing unrelated modifications into the same commit.

Use descriptive commit messages.

Examples:

```
Add TrueNAS engineering notebook

Document Nextcloud migration

Improve homepage accessibility

Update Plaid integration documentation
```

---

# Commit Philosophy

Every commit should represent one logical change.

Small commits are preferred over large unrelated commits.

---

# Engineering Notebook Standards

Every application should eventually have:

Application notebook (.http)

Runbook

Architecture document

Vendor documentation

Recovery procedure

---

# Automation

Automate repetitive work whenever practical.

Scripts should be:

Idempotent

Documented

Version controlled

---

# Change Management

Before major infrastructure changes:

Take snapshots.

Verify backups.

Document the change.

Perform verification.

Record lessons learned.

---

# Long-Term Vision

Midwest24 Core should be fully reproducible from version-controlled documentation.

A qualified engineer should be capable of rebuilding the platform using this repository and the Operations Manual.

This repository is intended to become the authoritative engineering knowledge base for Midwest24 Core.
