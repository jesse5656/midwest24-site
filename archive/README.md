# Midwest24 Archive

Midwest24 Archive is the institutional knowledge subsystem of Midwest24 Core.

## Purpose

Archive ingests, organizes, preserves, searches, and retrieves organizational knowledge.

## Current Architecture

- FastAPI backend
- PostgreSQL database
- SQLAlchemy ORM
- Alembic migrations
- Docker Compose development environment

## Current Domain Objects

- Entity
- Relationship
- Tag
- EntityTag
- Document
- ProcessingJob

## Current Capabilities

- Entity CRUD
- Relationship management
- Tagging
- Entity search
- Context retrieval
- Document upload
- Processing job queue

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
