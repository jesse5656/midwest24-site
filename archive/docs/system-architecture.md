# Midwest24 Archive — System Architecture

## Architecture Summary

Midwest24 Archive is a modular web application with a React frontend, FastAPI backend, PostgreSQL metadata store, S3-compatible object storage, and search/indexing layer.

## High-Level Flow

Browser
→ React Frontend
→ FastAPI REST API
→ Service Layer
→ Repository Layer
→ PostgreSQL / Object Storage / Search

## Core Principle

Archive organizes knowledge, not files.

Files are evidence. Metadata is structure. Relationships create institutional memory.

## Major Subsystems

- Frontend application
- REST API
- Authentication and authorization
- Metadata database
- Object storage
- Search index
- Audit logging
- AI-ready indexing pipeline
- Deployment infrastructure

## Storage Separation

PostgreSQL stores:

- archive entities
- metadata
- relationships
- permissions
- audit logs
- search fields

Object storage stores:

- original files
- previews
- thumbnails
- extracted text
- generated artifacts

Original files are immutable after ingestion.
