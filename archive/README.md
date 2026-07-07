# Midwest24 Archive

## Purpose

Midwest24 Archive is the institutional knowledge subsystem of Midwest24 Core.

Its responsibility is to ingest, organize, preserve, and retrieve organizational knowledge.

---

## Current Architecture

- PostgreSQL
- FastAPI
- SQLAlchemy
- Alembic
- Docker

---

## Domain Objects

- Entity
- Relationship
- Tag
- EntityTag
- Document
- ProcessingJob

---

## Current Capabilities

- Entity CRUD
- Relationship management
- Tagging
- Entity search
- Context retrieval
- Document upload
- Processing job queue

---

## Planned Pipeline

Upload
→ Processing Job
→ Text Extraction
→ OCR
→ Chunking
→ Embeddings
→ Semantic Search
→ Knowledge Graph
→ AI Retrieval
