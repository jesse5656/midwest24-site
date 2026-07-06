# Midwest24 Core Engineering Documentation

## Purpose

The `Tools` directory contains the engineering knowledge base for the Midwest24 Core platform.

Unlike the Operations Manual, which documents architecture, standards, and policies, this directory contains practical resources used during day-to-day engineering, development, deployment, and disaster recovery.

The goal is to ensure that every component of the platform can be maintained, rebuilt, and expanded using version-controlled documentation stored alongside the source code.

---

# Directory Structure

```
Tools/

api/
runbooks/
diagrams/
templates/
scripts/
```

---

# api

Application-specific engineering notebooks.

Contents include:

- REST API requests
- Authentication examples
- Health checks
- Common administrative commands
- Operational notes
- Vendor documentation links

Primary audience:

- Developers
- Infrastructure engineers
- System administrators

---

# runbooks

Step-by-step operational procedures.

Examples:

- Nextcloud migration
- Disaster recovery
- Storage expansion
- Google Drive migration
- Authentik deployment

Primary audience:

- Operations
- Infrastructure
- Disaster recovery

---

# diagrams

Architecture documentation.

Examples:

- Infrastructure
- Storage
- Authentication
- Networking
- Security
- Data flow

Diagrams should be maintained as Draw.io source files whenever possible.

---

# templates

Reusable documentation templates.

Examples:

- Runbooks
- Incident reports
- API notebooks
- Change requests
- Project kickoffs

---

# scripts

Supporting automation used during engineering work.

Scripts should be idempotent whenever practical and include documentation at the top of the file.

---

# Relationship to the Operations Manual

The Operations Manual explains:

> Why the platform is designed the way it is.

The documentation inside `Tools/` explains:

> How to operate, troubleshoot, and extend the platform.

Together they provide complete engineering documentation.

---

# Documentation Philosophy

Documentation should be:

- Accurate
- Version controlled
- Searchable
- Repeatable
- Practical

No production system should exist without accompanying engineering documentation.
