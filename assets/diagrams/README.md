# Midwest24 Architecture Diagrams

## Purpose

This directory contains the canonical architecture diagrams for the Midwest24 platform.

The `.excalidraw` files are the authoritative editable source.

The exported `.svg` and `.png` files are publication artifacts intended for MkDocs, GitHub, documentation, presentations, and operational references.

---

# Directory Structure

assets/
└── diagrams/
    ├── README.md
    ├── source/
    └── exports/

---

# Diagram Standards

- `.excalidraw` files are the source of truth.
- `.svg` files are preferred for documentation.
- `.png` files are publication exports.
- Never edit exported files manually.
- Regenerate exports after modifying an Excalidraw source file.

---

# Diagram Catalog

| ID | Diagram | Purpose |
|----|---------|---------|
| 001 | Conceptual Architecture | Executive overview of Midwest24 Core. |
| 002 | Logical Architecture | Platform components and relationships. |
| 003 | Physical Architecture | Hardware and infrastructure. |
| 004 | Deployment Architecture | Containers and runtime deployment. |
| 005 | Data Flow Architecture | Data movement throughout the platform. |
| 006 | Security Architecture | Identity, trust boundaries, and authorization. |
| 007 | Network Architecture | VLANs, routing, and connectivity. |
| 008 | Storage Architecture | ZFS, snapshots, replication, and backup. |
| 009 | AI Platform Architecture | AI cluster, models, embeddings, and agents. |
| 010 | Repository Intelligence Architecture | Knowledge graph, semantic search, and release intelligence. |

Future diagrams should continue sequential numbering.

---

# Naming Convention

Source:

001-conceptual-architecture.excalidraw

Exports:

001-conceptual-architecture.svg
001-conceptual-architecture.png

---

# Engineering Principles

- One diagram should communicate one architectural concern.
- Diagrams should become progressively more detailed.
- Maintain consistent naming and terminology.
- Update diagrams whenever architecture changes are approved.
- Architecture changes require an Architecture Change Proposal (ACP).

---

# Repository Standard

The `.excalidraw` file is the authoritative engineering artifact.

The exported `.svg` file is the documentation artifact referenced by MkDocs.

The exported `.png` file is intended for presentations and environments where SVG is not supported.
